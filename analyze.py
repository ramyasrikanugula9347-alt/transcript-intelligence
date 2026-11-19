"""Offline transcript intelligence baseline. Run with --dataset and --output."""
import argparse, csv, json, re
from pathlib import Path
from collections import Counter, defaultdict

# Keep the original five themes, but match the actual spoken text.
TOPICS = {
 'Reliability & Incidents': r'outages?|incidents?|downtime|failures?|failed|reliability|backups?|latency|performance|queue|degradation',
 'Security & Compliance': r'compliance|audits?|soc\s*2|pci|security|hipaa|gdpr|threats?|evidence|vulnerabilit\w*',
 'Commercial & Retention': r'renewals?|churn|pricing|upsell|billing|invoices?|contracts?|retention|discounts?|budget',
 'Product & Features': r'products?|features?|roadmap|launch\w*|sprints?|bug fixes?|onboarding|adoption|feedback',
 'Identity & Integrations': r'sso|saml|scim|integrations?|identity|mfa|ldap|provision\w*|authentication|connectors?',
}
PATTERNS = {k: re.compile(r'\b(?:'+v+r')\b', re.I) for k,v in TOPICS.items()}
RISK = re.compile(r'\b(?:outage|incident|escalation|urgent|churn|renewal risk|failure|customer impact)\b',re.I)
LABELS = ('positive','neutral','negative','unknown')
TYPES = ('Support','Internal','External')
def classify_call(info):
    # Preserve the original call-type rules so the sentiment comparison is consistent.
    emails = info['allEmails']
    if not emails: raise ValueError('Missing participant emails')
    if all(e.lower().endswith('@aegiscloud.com') for e in emails): return 'Internal'
    if info['title'].lower().startswith(('support case','urgent:','escalation:')): return 'Support'
    return 'External'
def load(path):
    return json.loads(path.read_text(encoding='utf-8'))
def save_csv(path, rows):
    if not rows: return
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
def analyze(dataset, output):
    output.mkdir(parents=True,exist_ok=True)
    folders=sorted(p for p in dataset.iterdir() if p.is_dir())
    if not folders: raise ValueError('No meeting folders found')
    meetings=[]; evidence=[]; risks=[]; counts=defaultdict(Counter); monthly=defaultdict(Counter); topic_counts=Counter(); topic_segments=Counter(); unmatched_segments=0; total_actions=0; all_actions=0; seen=set()
    for folder in folders:
        info=load(folder/'meeting-info.json'); summary=load(folder/'summary.json'); utterances=load(folder/'transcript.json')['data']
        mid=info['meetingId']; title=info['title']; kind=classify_call(info); month=info['startTime'][:7]
        if mid in seen: raise ValueError(f'Duplicate meeting ID: {mid}')
        seen.add(mid); sentiment=Counter(); matched=set()
        for item in utterances:
            text=item['sentence']; label=item.get('sentimentType','unknown').lower(); label=label if label in LABELS else 'unknown'
            sentiment[label]+=1
            tags=[topic for topic, pattern in PATTERNS.items() if pattern.search(text)]
            if not tags: unmatched_segments+=1
            for topic in tags:
                matched.add(topic); topic_segments[topic]+=1
                evidence.append(dict(topic=topic,meeting_id=mid,title=title,call_type=kind,time_seconds=item.get('time'),speaker=item.get('speaker_name'),text=text,sentiment=label))
        topic_counts.update(matched); counts[kind].update(sentiment); monthly[(month,kind)].update(sentiment)
        actions=summary.get('actionItems',[]); total_actions+=len(actions); all_actions+=bool(actions)
        for action in actions:
            if RISK.search(str(action)):
                risks.append(dict(meeting_id=mid,title=title,call_type=kind,action=str(action)))
        meetings.append(dict(meeting_id=mid,title=title,call_type=kind,month=month,segments=len(utterances),**{l:sentiment[l] for l in LABELS},topics='; '.join(t for t in TOPICS if t in matched),action_items=len(actions)))
    rows=[]
    for kind in TYPES:
        c=counts[kind]; n=sum(c.values()); rows.append(dict(call_type=kind,meetings=sum(m['call_type']==kind for m in meetings),segments=n,**{l:c[l] for l in LABELS},**{l+'_pct':round(100*c[l]/n,2) if n else 0 for l in LABELS}))
    months=[]
    for (month,kind),c in sorted(monthly.items()):
        n=sum(c.values()); months.append(dict(month=month,call_type=kind,segments=n,negative_pct=round(100*c['negative']/n,2) if n else 0))
    topics=[dict(topic=t,meetings=topic_counts[t],segments=topic_segments[t]) for t in TOPICS]
    for name,data in [('meetings',meetings),('sentiment_by_type',rows),('monthly_sentiment',months),('topics',topics),('topic_evidence',evidence),('risk_actions',risks)]: save_csv(output/(name+'.csv'),data)
    overall=sum(counts.values(),Counter()); result=dict(meetings=len(meetings),segments=sum(overall.values()),overall=dict(overall),sentiment=rows,monthly=months,topics=topics,unmatched_meetings=sum(not m['topics'] for m in meetings),unmatched_segments=unmatched_segments,actions=total_actions,meetings_with_actions=all_actions,risk_actions=len(risks))
    (output/'metrics.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    # Charts use the same aggregated values exported to CSV.
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(9,4.5)); left=[0]*len(rows)
    for label,color in [('positive','#18866b'),('neutral','#a5b3c4'),('negative','#cf6351'),('unknown','#555555')]:
        vals=[r[label+'_pct'] for r in rows]; ax.barh([r['call_type'] for r in rows],vals,left=left,label=label.title(),color=color)
        for i,v in enumerate(vals):
            if v>=6: ax.text(left[i]+v/2,i,f'{v:.1f}%',ha='center',va='center',fontsize=11)
        left=[a+b for a,b in zip(left,vals)]
    ax.set_xlim(0,100); ax.set_xlabel('Share of speech segments (%)'); ax.legend(ncol=4,loc='upper center',bbox_to_anchor=(.5,1.14)); ax.invert_yaxis(); fig.tight_layout(); fig.savefig(output/'sentiment.png',dpi=160); plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4.5)); ordered=sorted(topics,key=lambda r:r['meetings']); bars=ax.barh([r['topic'] for r in ordered],[r['meetings'] for r in ordered],color='#287c90'); ax.bar_label(bars,padding=4); ax.set_xlim(0,108); ax.set_xlabel('Meetings with at least one matching speech segment'); fig.tight_layout(); fig.savefig(output/'topics.png',dpi=160); plt.close(fig)
    print(json.dumps(result,indent=2)); return result
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--dataset',type=Path,default=Path('interview-assignment/dataset')); p.add_argument('--output',type=Path,default=Path('outputs')); a=p.parse_args(); analyze(a.dataset,a.output)
