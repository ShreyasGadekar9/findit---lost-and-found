import { type FormEvent, type ReactNode, useMemo, useState } from 'react';
import { QueryClient, QueryClientProvider, useQueryClient } from '@tanstack/react-query';
import {
  getGetDashboardQueryKey,
  getGetItemsQueryKey,
  getGetMatchesQueryKey,
  getGetMessagesQueryKey,
  ItemStatus,
  useConfirmReturn,
  useCreateItem,
  useGetDashboard,
  useGetItems,
  useGetMatches,
  useGetMessages,
  useHealthCheck,
  useSendMessage,
  useVerifyMatch,
} from '@workspace/api-client-react';
import type { Item, Match, MessageRole, ReportInput } from '@workspace/api-client-react';
import {
  ArrowDownLeft, ArrowRight, ArrowUpRight, Check, CheckCircle2, ChevronDown,
  CircleHelp, Clock3, Compass, HeartHandshake, LoaderCircle, MapPin, MessageCircle,
  Plus, Search, ShieldCheck, Sparkles, X,
} from 'lucide-react';
import { Link, Route, Switch, useLocation, useParams } from 'wouter';

const queryClient = new QueryClient();

function Brand() {
  return <Link href="/" className="brand-link" data-testid="link-home">
    <span className="brand-mark"><Compass size={19} strokeWidth={2.2} /></span>
    <span>find<span className="brand-italic">it</span><small>LOST & FOUND</small></span>
  </Link>;
}

function Shell({ children }: { children: ReactNode }) {
  const [location] = useLocation();
  const { data: health, isLoading } = useHealthCheck();
  return <div className="min-h-[100dvh]">
    <header className="topbar">
      <div className="topbar-inner">
        <Brand />
        <nav className="main-nav" aria-label="Main navigation">
          <Link href="/" className={`nav-link ${location === '/' ? 'active' : ''}`} data-testid="link-overview">Overview</Link>
          <Link href="/reports" className={`nav-link ${location.startsWith('/reports') ? 'active' : ''}`} data-testid="link-reports">Browse reports</Link>
        </nav>
        <div className="topbar-end">
          <span className={`service-state ${health?.status === 'UP' || health?.status === 'ok' ? 'online' : ''}`} data-testid="status-api">
            <span className="live-dot" /> {isLoading ? 'Connecting' : health?.status ? 'Here to help' : 'Checking'}
          </span>
          <Link href="/reports" className="button button-dark button-small" data-testid="button-header-report">
            <Plus size={15} /> Make a report
          </Link>
        </div>
      </div>
    </header>
    <main>{children}</main>
    <footer className="footer">
      <div className="footer-inner">
        <Brand />
        <p>A little kindness goes a long way.</p>
        <span><ShieldCheck size={14} /> Your details stay private</span>
      </div>
    </footer>
  </div>;
}

function StatusPill({ status }: { status: string }) {
  const text = status === 'OPEN' ? 'Still looking' : status === 'MATCHED' ? 'Possible match' : status === 'RETURNED' ? 'Back where it belongs' : status.toLowerCase();
  return <span className={`status-pill status-${status.toLowerCase()}`} data-testid={`status-${status.toLowerCase()}`}>{text}</span>;
}

function TypeTag({ type }: { type: string }) {
  return <span className={`type-tag ${type === 'LOST' ? 'type-lost' : 'type-found'}`}>
    {type === 'LOST' ? <ArrowDownLeft size={13} /> : <ArrowUpRight size={13} />}
    {type === 'LOST' ? 'Lost' : 'Found'}
  </span>;
}

function LoadingRows({ count = 3 }: { count?: number }) {
  return <div className="skeleton-list" aria-label="Loading reports">{Array.from({ length: count }, (_, i) => <div className="skeleton-row" key={i}>
    <div className="skeleton-thumb" /><div className="skeleton-lines"><i /><i /><i /></div>
  </div>)}</div>;
}

function ErrorNotice({ message, retry }: { message: string; retry: () => void }) {
  return <div className="error-notice" role="alert">
    <div><CircleHelp size={18} /><span><strong>We couldn’t load this just now.</strong><small>{message}</small></span></div>
    <button className="button button-outline button-small" onClick={retry} data-testid="button-retry">Try again</button>
  </div>;
}

function ReportCard({ item, compact = false }: { item: Item; compact?: boolean }) {
  return <article className={`report-card ${compact ? 'report-card-compact' : ''}`} data-testid={`card-report-${item.id}`}>
    <div className="report-visual">
      {item.photoUrl ? <img src={item.photoUrl} alt="" /> : <span className="visual-initial">{item.title.trim().slice(0, 1).toUpperCase()}</span>}
      <TypeTag type={item.type} />
    </div>
    <div className="report-body">
      <div className="report-card-top"><span>{item.category}</span><StatusPill status={item.status} /></div>
      <h3>{item.title}</h3>
      <p className="report-description">{item.description}</p>
      <div className="report-meta"><span><MapPin size={13} />{item.location}</span><span><Clock3 size={13} />{formatDate(item.itemDate)}</span></div>
    </div>
  </article>;
}

function formatDate(date?: string) {
  if (!date) return 'Date not listed';
  const parsed = new Date(date);
  if (Number.isNaN(parsed.getTime())) return date;
  return new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric' }).format(parsed);
}

function HomePage() {
  const summary = useGetDashboard();
  const itemsQuery = useGetItems({ status: ItemStatus.OPEN });
  const matchesQuery = useGetMatches();
  const recent = useMemo(() => (itemsQuery.data ?? []).slice(0, 3), [itemsQuery.data]);
  return <div className="page-enter">
    <section className="hero home-hero">
      <div className="hero-copy home-hero-copy">
        <span className="eyebrow"><span className="eyebrow-line" /> A community that looks out for you</span>
        <h1>Lost something?<br /><em>Let’s bring it home.</em></h1>
        <p>Small things matter. FindIt connects the people who’ve misplaced something with the kind people who’ve found it.</p>
        <div className="hero-actions">
          <Link href="/reports" className="button button-dark" data-testid="button-find-item">Find an item <ArrowRight size={16} /></Link>
          <Link href="/reports" className="text-link" data-testid="button-report-item">I found something <ArrowUpRight size={16} /></Link>
        </div>
        <div className="privacy-note"><ShieldCheck size={16} /><span>Your contact details are never shown publicly.</span></div>
      </div>
      <div className="hero-key-stage" role="img" aria-label="A softly illuminated key, a small reminder that lost things can find their way home.">
        <div className="key-stage-word" aria-hidden="true">HOME</div>
        <div className="key-stage-index"><span>F / 01</span><span>FOUND, TOGETHER</span></div>
        <div
          className="key-interaction"
          onPointerMove={event => {
            if (event.pointerType !== 'mouse' || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
            const bounds = event.currentTarget.getBoundingClientRect();
            const x = (event.clientX - bounds.left) / bounds.width - 0.5;
            const y = (event.clientY - bounds.top) / bounds.height - 0.5;
            event.currentTarget.style.setProperty('--key-tilt-x', `${(-y * 12).toFixed(2)}deg`);
            event.currentTarget.style.setProperty('--key-tilt-y', `${(x * 14).toFixed(2)}deg`);
          }}
          onPointerLeave={event => {
            event.currentTarget.style.setProperty('--key-tilt-x', '0deg');
            event.currentTarget.style.setProperty('--key-tilt-y', '0deg');
          }}
          data-testid="hero-key"
        >
          <div className="key-float" aria-hidden="true">
            <div className="key-tilt">
              <svg className="hero-key-svg" viewBox="0 0 220 470" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <linearGradient id="key-metal" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0" stopColor="#f1d5a6" />
                    <stop offset=".28" stopColor="#c8905d" />
                    <stop offset=".56" stopColor="#e4b778" />
                    <stop offset="1" stopColor="#79543a" />
                  </linearGradient>
                  <linearGradient id="key-edge" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0" stopColor="#fff1d2" stopOpacity=".72" />
                    <stop offset=".22" stopColor="#fff1d2" stopOpacity="0" />
                    <stop offset=".78" stopColor="#553920" stopOpacity=".5" />
                    <stop offset="1" stopColor="#fff1d2" stopOpacity=".18" />
                  </linearGradient>
                </defs>
                <g fill="url(#key-metal)" stroke="url(#key-edge)" strokeWidth="2">
                  <path fillRule="evenodd" d="M110 18a75 75 0 1 0 0 150 75 75 0 0 0 0-150Zm0 28a47 47 0 1 1 0 94 47 47 0 0 1 0-94Z" />
                  <path d="M92 160h36v211h-36z" />
                  <path d="M91 330h82v34h-48v45h-36v-79Z" />
                  <path d="M91 399h56v32h-56z" />
                </g>
                <path d="M99 175v178m0 20v26" stroke="#fff0d1" strokeOpacity=".3" strokeWidth="3" />
                <circle cx="110" cy="93" r="62" fill="none" stroke="#fff0d1" strokeOpacity=".12" strokeWidth="2" />
              </svg>
            </div>
          </div>
        </div>
        <div className="key-stage-caption"><span className="caption-dot" />Little things find their way.</div>
        <span className="key-stage-orbit orbit-a" aria-hidden="true" />
        <span className="key-stage-orbit orbit-b" aria-hidden="true" />
      </div>
    </section>
    <section className="stats-strip" aria-label="FindIt community activity">
      {summary.isLoading ? <div className="stats-loading">Gathering the latest good news…</div> : summary.isError ? <ErrorNotice message="Community totals are unavailable." retry={() => summary.refetch()} /> :
        <><div className="stats-intro"><span className="eyebrow">THE KINDNESS COUNTER</span><p>Every report brings us<br />a little closer.</p></div>
        <Stat number={summary.data?.totalReports} label="community reports" />
        <Stat number={summary.data?.potentialMatches} label="possible connections" />
        <Stat number={summary.data?.returnedItems} label="items back home" warm /></>}
    </section>
    <section className="home-reports section-wrap">
      <div className="section-heading">
        <div><span className="eyebrow"><span className="eyebrow-line" /> THE LATEST</span><h2>Still looking for<br /><em>their person.</em></h2></div>
        <Link href="/reports" className="text-link" data-testid="link-all-reports">See all reports <ArrowRight size={16} /></Link>
      </div>
      {itemsQuery.isLoading ? <LoadingRows /> : itemsQuery.isError ? <ErrorNotice message="The latest reports aren’t available right now." retry={() => itemsQuery.refetch()} /> : recent.length === 0 ?
        <div className="empty-state"><div className="empty-icon"><HeartHandshake size={22} /></div><h3>A quiet moment for lost things.</h3><p>No open reports just yet. If something’s missing or found, you can start here.</p><Link href="/reports" className="button button-outline" data-testid="button-empty-report">Create a report <ArrowRight size={15} /></Link></div> :
        <div className="report-grid">{recent.map(item => <ReportCard key={item.id} item={item} />)}</div>}
    </section>
    <section className="match-band">
      <div className="match-band-mark"><HeartHandshake size={30} /></div>
      <div><span className="eyebrow">A GOOD THING IN MOTION</span><h2>Something might<br />already be waiting.</h2><p>We look for promising connections between lost and found reports.</p></div>
      <div className="match-band-side">
        {matchesQuery.isLoading ? <span className="match-count">Looking for connections…</span> : matchesQuery.isError ? <span className="match-count">Connections are taking a moment.</span> :
          <><strong>{matchesQuery.data?.filter(match => match.status !== 'RETURNED').length ?? 0}</strong><span>possible connections<br />being brought together</span></>}
        <Link href="/reports" className="button button-light" data-testid="button-explore-reports">Explore reports <ArrowRight size={15} /></Link>
      </div>
    </section>
  </div>;
}

function Stat({ number, label, warm = false }: { number?: number; label: string; warm?: boolean }) {
  return <div className={`stat-cell ${warm ? 'stat-warm' : ''}`}><strong data-testid={`stat-${label.replaceAll(' ', '-')}`}>{number ?? '—'}</strong><span>{label}</span></div>;
}

function ReportsPage() {
  const [search, setSearch] = useState('');
  const [type, setType] = useState('');
  const [showForm, setShowForm] = useState(false);
  const params = useMemo(() => ({ ...(type ? { type: type as 'LOST' | 'FOUND' } : {}), ...(search.trim() ? { q: search.trim() } : {}) }), [type, search]);
  const itemsQuery = useGetItems(params);
  const matchesQuery = useGetMatches();
  const filtered = itemsQuery.data ?? [];
  return <div className="reports-page page-enter">
    <div className="page-top section-wrap">
      <div><span className="eyebrow"><span className="eyebrow-line" /> THE COMMUNITY BOARD</span><h1>Things looking<br /><em>for their way home.</em></h1><p>Browse what’s been lost or found nearby. A little detail can make all the difference.</p></div>
      <div className="page-top-action"><span className="fine-print"><ShieldCheck size={14} /> Your details stay private</span><button className="button button-dark" onClick={() => setShowForm(true)} data-testid="button-new-report"><Plus size={16} /> Make a report</button></div>
    </div>
    <div className="section-wrap reports-content">
      {matchesQuery.data && matchesQuery.data.filter(match => match.status !== 'RETURNED').length > 0 && <div className="match-nudge" data-testid="text-potential-matches">
        <span className="nudge-icon"><Sparkles size={17} /></span><div><strong>There are promising connections</strong><p>Some lost and found reports may belong together. Review one when you’re ready.</p></div>
        <Link href={`/matches/${matchesQuery.data.find(match => match.status !== 'RETURNED')?.id}`} className="text-link">Review match <ArrowRight size={15} /></Link>
      </div>}
      <div className="filters-row">
        <label className="search-box"><Search size={17} /><input aria-label="Search reports" data-testid="input-search-reports" placeholder="Search an item, place or detail…" value={search} onChange={event => setSearch(event.target.value)} /><kbd>/</kbd></label>
        <div className="filter-group" role="group" aria-label="Filter report type">
          {[['', 'Everything'], ['LOST', 'Lost'], ['FOUND', 'Found']].map(([value, label]) => <button key={value} className={`filter-chip ${type === value ? 'selected' : ''}`} onClick={() => setType(value)} data-testid={`filter-${label.toLowerCase()}`}>{label}</button>)}
        </div>
      </div>
      <div className="results-heading"><span>{itemsQuery.data?.length ?? 0} {itemsQuery.data?.length === 1 ? 'report' : 'reports'}</span><span>Most recent first <ChevronDown size={14} /></span></div>
      {itemsQuery.isLoading ? <LoadingRows count={4} /> : itemsQuery.isError ? <ErrorNotice message="Reports could not be loaded." retry={() => itemsQuery.refetch()} /> : filtered.length === 0 ?
        <div className="empty-state reports-empty"><div className="empty-icon"><Search size={21} /></div><h3>No reports found this time.</h3><p>Try a different search, or share a report so the community can help.</p><button className="button button-outline" onClick={() => setShowForm(true)} data-testid="button-empty-create">Create a report <ArrowRight size={15} /></button></div> :
        <div className="report-grid">{filtered.map(item => <ReportCard key={item.id} item={item} />)}</div>}
    </div>
    {showForm && <CreateReportModal onClose={() => setShowForm(false)} />}
  </div>;
}

function CreateReportModal({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient();
  const createItem = useCreateItem();
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [type, setType] = useState<'LOST' | 'FOUND'>('LOST');
  const [fields, setFields] = useState({ reporter: '', title: '', category: '', description: '', location: '', itemDate: '', photoUrl: '', privateDetail: '' });
  function update(key: keyof typeof fields, value: string) { setFields(current => ({ ...current, [key]: value })); }
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError('');
    const payload: ReportInput = {
      ...fields,
      type,
      photoUrl: fields.photoUrl.trim() || null,
      privateDetail: type === 'LOST' ? fields.privateDetail.trim() : '',
    };
    createItem.mutate({ data: payload }, {
      onSuccess: async () => {
        await Promise.all([
          queryClient.invalidateQueries({ queryKey: getGetItemsQueryKey() }),
          queryClient.invalidateQueries({ queryKey: getGetDashboardQueryKey() }),
          queryClient.invalidateQueries({ queryKey: getGetMatchesQueryKey() }),
        ]);
        setSuccess(true);
      },
      onError: () => setError('Your report didn’t go through. Please check the details and try again.'),
    });
  }
  if (success) return <div className="modal-scrim" role="presentation" onMouseDown={event => { if (event.target === event.currentTarget) onClose(); }}>
    <section className="modal-card success-modal" role="dialog" aria-modal="true" aria-labelledby="report-success-title">
      <button className="modal-close" onClick={onClose} aria-label="Close" data-testid="button-close-success"><X size={18} /></button>
      <div className="success-mark"><CheckCircle2 size={27} /></div><span className="eyebrow">REPORT SHARED</span><h2 id="report-success-title">Thank you for<br /><em>looking out.</em></h2><p>Your report is on the community board. Private verification details are only used to confirm a match.</p><button className="button button-dark" onClick={onClose} data-testid="button-done-report">Back to reports <ArrowRight size={15} /></button>
    </section>
  </div>;
  return <div className="modal-scrim" role="presentation" onMouseDown={event => { if (event.target === event.currentTarget) onClose(); }}>
    <section className="modal-card report-modal" role="dialog" aria-modal="true" aria-labelledby="create-report-title">
      <button className="modal-close" onClick={onClose} aria-label="Close report form" data-testid="button-close-modal"><X size={18} /></button>
      <div className="modal-heading"><span className="eyebrow"><span className="eyebrow-line" /> START WITH THE DETAILS</span><h2 id="create-report-title">Let’s get it<br /><em>back where it belongs.</em></h2><p>Share what happened. We’ll help the right person find it.</p></div>
      <form onSubmit={submit} className="report-form">
        <div className="report-type-toggle" role="group" aria-label="Report type">
          <button type="button" className={type === 'LOST' ? 'chosen' : ''} onClick={() => setType('LOST')} data-testid="button-type-lost"><ArrowDownLeft size={15} /> I lost something</button>
          <button type="button" className={type === 'FOUND' ? 'chosen' : ''} onClick={() => setType('FOUND')} data-testid="button-type-found"><ArrowUpRight size={15} /> I found something</button>
        </div>
        <div className="form-grid">
          <Field label="Your name" required><input value={fields.reporter} onChange={e => update('reporter', e.target.value)} required maxLength={100} placeholder="What should we call you?" data-testid="input-reporter" /></Field>
          <Field label="Item name" required><input value={fields.title} onChange={e => update('title', e.target.value)} required minLength={2} maxLength={140} placeholder="A blue canvas backpack" data-testid="input-item-title" /></Field>
          <Field label="Category" required><input value={fields.category} onChange={e => update('category', e.target.value)} required maxLength={64} placeholder="Bags, keys, clothing…" data-testid="input-category" /></Field>
          <Field label="Where?" required><input value={fields.location} onChange={e => update('location', e.target.value)} required minLength={2} maxLength={180} placeholder="A place or nearby landmark" data-testid="input-location" /></Field>
          <Field label="When?" required><input type="date" value={fields.itemDate} onChange={e => update('itemDate', e.target.value)} required data-testid="input-item-date" /></Field>
          <Field label="Photo link" optional><input type="url" value={fields.photoUrl} onChange={e => update('photoUrl', e.target.value)} maxLength={500} placeholder="https://…" data-testid="input-photo-url" /></Field>
          <Field label="A few more details" required wide><textarea value={fields.description} onChange={e => update('description', e.target.value)} required minLength={4} maxLength={1000} rows={3} placeholder="Color, marks, what was inside — anything that could help someone recognize it." data-testid="input-description" /></Field>
          {type === 'LOST' && <Field label="A private detail only you would know" required wide><input value={fields.privateDetail} onChange={e => update('privateDetail', e.target.value)} required minLength={2} maxLength={180} placeholder="For verification only — never shown on the public report" data-testid="input-private-detail" /><small className="field-hint"><ShieldCheck size={13} /> This stays private and helps us check that a match is really yours.</small></Field>}
        </div>
        {error && <div className="form-error" role="alert">{error}</div>}
        <div className="form-footer"><span><ShieldCheck size={14} /> Contact information is never made public.</span><button className="button button-dark" type="submit" disabled={createItem.isPending} data-testid="button-submit-report">{createItem.isPending ? <><LoaderCircle className="spin" size={16} /> Sharing…</> : <>Share report <ArrowRight size={15} /></>}</button></div>
      </form>
    </section>
  </div>;
}

function Field({ label, required, optional, wide, children }: { label: string; required?: boolean; optional?: boolean; wide?: boolean; children: ReactNode }) {
  return <label className={`field ${wide ? 'field-wide' : ''}`}><span>{label}{required && <b> *</b>}{optional && <i> optional</i>}</span>{children}</label>;
}

function MatchPage() {
  const params = useParams<{ matchId: string }>();
  const matchId = Number(params.matchId);
  const matches = useGetMatches();
  const match = matches.data?.find(item => item.id === matchId);
  return <div className="match-page page-enter section-wrap">
    <Link href="/reports" className="back-link" data-testid="link-back-reports"><ArrowDownLeft size={15} /> Back to reports</Link>
    {matches.isLoading ? <LoadingRows count={2} /> : matches.isError ? <ErrorNotice message="We couldn’t load this possible match." retry={() => matches.refetch()} /> : !match ?
      <div className="empty-state"><div className="empty-icon"><Search size={21} /></div><h3>This match isn’t available.</h3><p>It may have already been resolved, or the link may be out of date.</p><Link href="/reports" className="button button-dark" data-testid="button-match-not-found">Browse reports <ArrowRight size={15} /></Link></div> : <MatchWorkspace match={match} />}
  </div>;
}

function MatchWorkspace({ match }: { match: Match }) {
  const [privateDetail, setPrivateDetail] = useState('');
  const [role, setRole] = useState<MessageRole>('OWNER');
  const [senderName, setSenderName] = useState('');
  const [text, setText] = useState('');
  const [notice, setNotice] = useState('');
  const [problem, setProblem] = useState('');
  const queryClient = useQueryClient();
  const matchId = match.id;
  const messagesQuery = useGetMessages(matchId, { query: { enabled: match.verified, queryKey: getGetMessagesQueryKey(matchId) } });
  const verifyMatch = useVerifyMatch();
  const sendMessage = useSendMessage();
  const confirmReturn = useConfirmReturn();
  const messages = messagesQuery.data ?? [];
  const returned = match.status === 'RETURNED' || (match.lostConfirmed && match.foundConfirmed);
  const waitingOnOther = match.lostConfirmed !== match.foundConfirmed;
  async function refreshMatchData() {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: getGetMatchesQueryKey() }),
      queryClient.invalidateQueries({ queryKey: getGetDashboardQueryKey() }),
    ]);
  }
  function verify(event: FormEvent) {
    event.preventDefault(); setProblem(''); setNotice('');
    verifyMatch.mutate({ matchId, data: { privateDetail } }, {
      onSuccess: async result => { setNotice(result.message || 'That’s a match. You’re verified.'); setPrivateDetail(''); await refreshMatchData(); },
      onError: () => setProblem('That detail didn’t match. Check it and try again.'),
    });
  }
  function submitMessage(event: FormEvent) {
    event.preventDefault(); if (!text.trim() || !senderName.trim()) return;
    setProblem('');
    sendMessage.mutate({ matchId, data: { role, senderName: senderName.trim(), text: text.trim() } }, {
      onSuccess: async () => { setText(''); await queryClient.invalidateQueries({ queryKey: getGetMessagesQueryKey(matchId) }); },
      onError: () => setProblem('Your message couldn’t be sent. Please try again.'),
    });
  }
  function confirm() {
    setProblem('');
    confirmReturn.mutate({ matchId, data: { role } }, {
      onSuccess: async () => { setNotice('Thanks for confirming. We’ve updated this return.'); await refreshMatchData(); },
      onError: () => setProblem('We couldn’t save your confirmation. Please try again.'),
    });
  }
  return <div className="match-workspace">
    <div className="match-title-row"><div><span className="eyebrow"><span className="eyebrow-line" /> A POSSIBLE CONNECTION</span><h1>Could this be<br /><em>the one?</em></h1><p>Compare the details, then verify privately before arranging a hand-off.</p></div><div className="match-score"><Sparkles size={18} /><strong>{Math.round(match.score * (match.score <= 1 ? 100 : 1))}%</strong><span>similarity</span></div></div>
    <div className="match-pair">
      <MatchItem item={match.lostItem} />
      <div className="pair-connector"><span><HeartHandshake size={19} /></span><i /></div>
      <MatchItem item={match.foundItem} />
    </div>
    {!match.verified && !returned && <section className="verify-panel">
      <div className="verify-ornament"><ShieldCheck size={23} /></div><div className="verify-copy"><span className="eyebrow">A PRIVATE CHECK</span><h2>Know one detail<br /><em>that isn’t listed?</em></h2><p>Only the person who reported the item should know this. It won’t appear in your public report or chat.</p></div>
      <form className="verify-form" onSubmit={verify}><label htmlFor="verify-detail">Private verification detail</label><input id="verify-detail" value={privateDetail} onChange={e => setPrivateDetail(e.target.value)} required minLength={1} maxLength={180} placeholder="Enter the detail from your report" data-testid="input-verify-detail" /><button className="button button-dark" type="submit" disabled={verifyMatch.isPending} data-testid="button-verify-match">{verifyMatch.isPending ? <><LoaderCircle className="spin" size={15} /> Checking…</> : <>Verify this match <ArrowRight size={15} /></>}</button></form>
    </section>}
    {match.verified && <section className="conversation-section">
      <div className="conversation-top"><div><span className="eyebrow"><span className="eyebrow-line" /> VERIFIED CONNECTION</span><h2>Make the <em>handoff.</em></h2></div><span className="verified-badge"><CheckCircle2 size={15} /> Verified</span></div>
      <div className="conversation-grid">
        <div className="chat-panel">
          <div className="chat-heading"><MessageCircle size={17} /><span>Private conversation</span><span className="private-chip"><ShieldCheck size={12} /> Private</span></div>
          {messagesQuery.isLoading ? <div className="chat-loading"><span /><span /><span /></div> : messagesQuery.isError ? <ErrorNotice message="Conversation could not be loaded." retry={() => messagesQuery.refetch()} /> : messages.length === 0 ?
            <div className="chat-empty"><div className="chat-empty-mark"><MessageCircle size={20} /></div><strong>Start with a hello.</strong><p>Keep contact details private. Arrange a safe, public hand-off together.</p></div> :
            <div className="message-list">{messages.map(message => <div key={message.id} className={`message-bubble ${message.role === role ? 'mine' : ''}`} data-testid={`message-${message.id}`}><div className="message-meta"><strong>{message.senderName}</strong><span>{formatDate(message.sentAt)}</span></div><p>{message.text}</p></div>)}</div>}
          <form className="chat-form" onSubmit={submitMessage}>
            <div className="chat-input-top"><select value={role} onChange={e => setRole(e.target.value as MessageRole)} aria-label="Your role" data-testid="select-message-role"><option value="OWNER">I’m the owner</option><option value="FINDER">I’m the finder</option></select><input aria-label="Your name" placeholder="Your name" value={senderName} onChange={e => setSenderName(e.target.value)} maxLength={100} required data-testid="input-chat-name" /></div>
            <div className="chat-compose"><input aria-label="Write a message" placeholder="Write a thoughtful message…" value={text} onChange={e => setText(e.target.value)} maxLength={1000} required data-testid="input-chat-message" /><button type="submit" className="send-button" aria-label="Send message" disabled={sendMessage.isPending} data-testid="button-send-message">{sendMessage.isPending ? <LoaderCircle className="spin" size={17} /> : <ArrowRight size={17} />}</button></div>
          </form>
        </div>
        <aside className="return-panel">
          <div className="return-icon">{returned ? <Check size={20} /> : <HeartHandshake size={20} />}</div>
          <span className="eyebrow">THE LAST LITTLE STEP</span>
          <h3>{returned ? 'Back where it belongs.' : 'Made the hand-off?'}</h3>
          <p>{returned ? 'Both sides have confirmed this item made it home.' : waitingOnOther ? 'Your confirmation is in. The other person can confirm when they’re ready.' : 'Once the item is safely returned, either person can confirm it here.'}</p>
          <label className="return-role-label" htmlFor="return-role">Confirming as</label>
          <select id="return-role" value={role} onChange={e => setRole(e.target.value as MessageRole)} disabled={returned} data-testid="select-return-role"><option value="OWNER">The owner</option><option value="FINDER">The finder</option></select>
          <button className={`button ${returned ? 'button-outline' : 'button-dark'} return-confirm-button`} disabled={returned || (role === 'OWNER' ? match.lostConfirmed : match.foundConfirmed) || confirmReturn.isPending} onClick={confirm} data-testid="button-confirm-return">
            {confirmReturn.isPending ? <><LoaderCircle className="spin" size={15} /> Saving…</> : returned ? <><Check size={15} /> Return confirmed</> : role === 'OWNER' ? match.lostConfirmed ? 'Owner confirmed' : 'Confirm I have it' : match.foundConfirmed ? 'Finder confirmed' : 'Confirm it’s returned'}
          </button>
          <div className="confirmation-progress"><span className={match.lostConfirmed ? 'complete' : ''}><Check size={11} /> Owner</span><i /><span className={match.foundConfirmed ? 'complete' : ''}><Check size={11} /> Finder</span></div>
        </aside>
      </div>
    </section>}
    {notice && <div className="match-notice" role="status"><CheckCircle2 size={17} />{notice}<button onClick={() => setNotice('')} aria-label="Dismiss message"><X size={15} /></button></div>}
    {problem && <div className="form-error match-error" role="alert">{problem}</div>}
  </div>;
}

function MatchItem({ item }: { item: Item }) {
  return <article className="match-item-card"><div className="match-item-visual">{item.photoUrl ? <img src={item.photoUrl} alt="" /> : <span>{item.title.trim().slice(0, 1).toUpperCase()}</span>}<TypeTag type={item.type} /></div><div className="match-item-info"><span className="item-category">{item.category}</span><h3>{item.title}</h3><p>{item.description}</p><div className="report-meta"><span><MapPin size={13} />{item.location}</span><span><Clock3 size={13} />{formatDate(item.itemDate)}</span></div><StatusPill status={item.status} /></div></article>;
}

function NotFound() {
  return <div className="not-found"><span className="eyebrow">A SMALL DETOUR</span><h1>That page wandered off.</h1><p>Let’s get you back to the community board.</p><Link href="/" className="button button-dark" data-testid="link-not-found-home">Go home <ArrowRight size={15} /></Link></div>;
}

function App() {
  return <QueryClientProvider client={queryClient}>
    <Shell><Switch>
      <Route path="/" component={HomePage} />
      <Route path="/reports" component={ReportsPage} />
      <Route path="/matches/:matchId" component={MatchPage} />
      <Route component={NotFound} />
    </Switch></Shell>
  </QueryClientProvider>;
}

export default App;
