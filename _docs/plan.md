# TeamRetroLoop — MVP Product & Technical Plan

## 1. Product definition

**TeamRetroLoop** is a web application for software development teams to run facilitated sprint retrospectives. It helps a team privately share **Start / Stop / Continue** feedback, reveal it fairly, collaboratively cluster it into topics, prioritize topics through voting, discuss them, record decisions and action items, and review those actions in the next retrospective.

**Product principle:** AI assists the team and facilitator; it does not replace their judgment or participate in the live discussion in the MVP.

## 2. Goals and problems addressed

The MVP is intended to make retrospectives more structured and outcome-oriented by supporting a complete loop:

1. Capture candid feedback privately.
2. Make feedback visible to everyone at the same time.
3. Help the team identify and prioritize the issues worth discussing.
4. Preserve decisions separately from follow-up work.
5. Ensure action items are owned, tracked, and reviewed in the next retro.

The product is team-centric, supports a user belonging to multiple teams, and is designed for real-time collaborative retrospectives led by a session facilitator.

## 3. Users and roles

### Authenticated user

- Can log in/out and maintain a user profile.
- May belong to multiple teams.
- Can participate in retros for teams they belong to.
- Can be made facilitator for a particular retro; facilitator is a **session-level responsibility**, not a permanent product role.

### Team manager / team lead

- Can manage team membership.
- The precise team-management permission model is TBD.

### Facilitator (per retro session)

- Creates and schedules a retro for a team.
- Selects the sprint and facilitator.
- Starts and ends the session/stages.
- Invites or enables participants to join through the dashboard and/or link (delivery and invitation rules are TBD).
- Reveals all feedback at once.
- Guides the flow from clustering through voting, discussion, decisions, actions, summary, and closure.

### Participant

- Contributes feedback, choosing identified or anonymous attribution per card.
- Collaboratively clusters visible cards into topics.
- Receives three votes to distribute across discussion topics.
- Participates in discussion and can contribute to decisions and action items.

## 4. Authoritative core workflow

```text
Create Retro
  → Invite / join team
  → Private feedback collection
  → Reveal all cards simultaneously
  → Collaborative clustering into topics
  → Three votes per person (multiple votes on one topic allowed)
  → Select and discuss topics
  → Record decisions and action items
  → Close retro
  → Track actions
  → Next retro: review prior actions and their effectiveness
```

## 5. MVP scope and detailed features

### 5.1 Users and teams

- Authentication: login and logout.
- User profile.
- Teams and team members.
- A user can belong to multiple teams.
- A manager/team lead can manage a team.
- No organization-wide administration is required in the MVP.

### 5.2 Retro sessions

- Create a retro for a team.
- Record/select a sprint.
- Set a facilitator and schedule/date.
- Facilitator starts and ends the session.
- Participants join from the dashboard and/or a link.
- Display real-time participant presence.
- Manual sprint information is in scope; external sprint-system integrations are not.

The final required setup fields beyond team, sprint, date/time, and facilitator are TBD. Preparation before the live session is also TBD.

### 5.3 Feedback

The only feedback format in the MVP is:

- **Start** — what the team should start doing.
- **Stop** — what the team should stop doing.
- **Continue** — what the team should continue doing.

Each feedback card records:

- Category.
- Feedback text.
- Author (held internally).
- Anonymous flag.
- Creation time.

Names appear by default. A contributor may choose to make an individual card anonymous. Earlier ideas to include Wins and Kudos as separate MVP categories are superseded by this final three-category decision.

### 5.4 Feedback reveal

- During collection, a participant sees only their own cards.
- No participant sees other participants’ cards before reveal.
- The facilitator triggers **Reveal Feedback**.
- All submitted cards appear to the team at the same time.
- There is no gradual or selective facilitator reveal.

### 5.5 Collaborative clustering

- After reveal, the team collaboratively groups feedback cards into discussion topics.
- The team is responsible for the final grouping.
- The exact interaction design, editing/conflict rules, and whether a facilitator has any override are TBD.

### 5.6 Voting

- Voting occurs after clustering.
- Each participant has exactly **three votes**.
- Votes are cast on topics, not defined as thumbs-up/down reactions on individual feedback cards.
- A participant may distribute votes across topics or allocate multiple/all three to a single topic.
- Vote totals prioritize candidates for discussion.
- The facilitator guides the team into discussion after voting.
- The timing/visibility of vote totals before voting closes is TBD.

### 5.7 Discussion

- The facilitator selects topics for discussion, informed by voting.
- Participants can comment/contribute in a simple discussion area.
- Capture discussion notes.
- Mark a topic as discussed.
- AI does not participate in or interrupt live discussion in the MVP.

### 5.8 Decisions and action items

A discussion may produce a decision, an action item, both, or neither. A decision is not automatically an action.

Action item fields:

- Title.
- Description.
- Owner.
- Due date.
- Priority.
- Status: Open, In Progress, Completed, or Cancelled.
- Link to the originating retro and topic.

The system should preserve these links so the team can understand why an action exists. The precise decision data model is TBD, but decisions must be recorded as part of the discussion outcome.

### 5.9 The retro loop

At the beginning of the next retro, show prior actions with their status:

- Completed.
- In Progress.
- Not Started.
- Overdue.

The team can record whether an action helped. This action-effectiveness review is a core MVP feature.

`Not Started` and `Overdue` are review/display states; how they map to the persisted action status and due date is TBD.

### 5.10 AI assistance

AI is optional assistance only. Every AI suggestion requires human approval.

MVP AI capabilities:

- Suggest clusters of similar feedback cards.
- Suggest themes.
- Summarize feedback.
- Suggest discussion topics.
- Summarize discussions and decisions.
- Generate a final retro summary.
- Use historic retrospectives to help identify patterns, where sufficient history exists.

AI clustering is not mandatory and must not silently determine the final board. No AI facilitator, live-discussion intervention, predictive team-health scoring, or autonomous action creation is in scope.

### 5.11 Attachments

After the meeting, the facilitator can attach one or more of:

- Audio.
- Video.
- Transcript.

Attachments belong to the retro. Built-in recording, media playback, and transcription are not MVP requirements. AI analysis of an uploaded transcript is a future possibility, not a committed MVP feature.

### 5.12 History

- Basic team-level retrospective history.
- Previous retrospectives, feedback/themes, actions, and retro summaries.
- Action tracking and the previous-action review at the start of the next retro.
- Advanced analytics, reporting, and exports are excluded.

### 5.13 APIs

- REST APIs using Django REST Framework (DRF).
- Authentication and authorization.
- APIs for the major entities: users, teams, memberships, retros, participation, feedback, topics/clusters, votes, discussions, decisions, actions, attachments, summaries, and history.
- OpenAPI/Swagger documentation.
- API-first design so a web UI is one API consumer and future clients/integrations remain possible.

## 6. Permissions and visibility rules

| Area | MVP rule |
|---|---|
| Access | Users must authenticate; team/retro access is limited to appropriate team members. Detailed authorization matrix is TBD. |
| Team management | A manager/team lead can manage the team. Exact create/remove/manage boundaries are TBD. |
| Facilitator | Assigned per session and controls session progression/reveal. |
| Feedback before reveal | Every participant sees only their own cards. |
| Feedback after reveal | All cards become visible to the team simultaneously. |
| Attribution | Identified by default; contributor can set a card anonymous. The system retains author information internally. Who, if anyone, can access it is TBD. |
| AI | Suggestions require human approval; AI has no authority to finalize groups, decisions, or actions. |
| Attachments/history | Access scope and retention policy are TBD. |

## 7. Real-time collaboration

Real-time collaboration is essential to the product experience. The application should provide live updates for:

- Participant presence in a retro.
- Session-stage changes initiated by the facilitator.
- A participant’s own feedback collection experience, while preserving pre-reveal privacy.
- The simultaneous reveal transition.
- Collaborative clustering changes.
- Vote submissions and any authorized vote-result updates.
- Discussion notes/status and action-item changes.

The authorization rules must be enforced server-side for both REST and WebSocket messages. Exact collaboration conflict-resolution behavior is TBD.

## 8. Proposed screens

Core live workflow:

1. Login.
2. Dashboard.
3. Retro setup.
4. Retro lobby.
5. Feedback collection.
6. Feedback reveal and clustering board.
7. Voting and discussion.
8. Retro summary and actions.

Supporting screens:

9. Team management.
10. Retro history.
11. Action tracking.

## 9. Session lifecycle

The initial proposed lifecycle is refined below to reflect the final workflow:

```text
Draft
  → Lobby / scheduled
  → Collecting feedback
  → Revealed / clustering
  → Voting
  → Discussion
  → Action planning and summary
  → Closed
```

- The facilitator moves the retro through stages.
- Reveal is an explicit boundary between private collection and shared content.
- The final distinction between a scheduled session and lobby, whether stages can be reopened, and closure/summary editing rules are TBD.

## 10. Suggested technical architecture

This is a proposed implementation architecture, not a product decision beyond the stated Django preference.

```text
Web client
  ├─ REST API ───────────────┐
  └─ WebSockets ─────────────┤
                             ▼
Django application
  ├─ Django REST Framework (REST APIs and OpenAPI/Swagger)
  ├─ Django Channels (real-time WebSocket collaboration)
  ├─ Domain modules: identity, teams, retros, feedback, clustering,
  │  voting, discussion, decisions/actions, attachments, history, AI
  ├─ Celery (background jobs: AI requests, summary generation,
  │  attachment-related processing as needed)
  └─ PostgreSQL (durable relational data)
          │
          └─ Redis (Channels layer, Celery broker/result support, caching)
```

Suggested implementation considerations:

- PostgreSQL stores the relational source of truth, including team membership, session stage, feedback visibility state, votes, decisions, actions, and audit-relevant timestamps.
- Django Channels/WebSockets support authenticated, team-scoped live events.
- Celery moves non-interactive work such as AI grouping/summarization out of the request path.
- Redis supports the real-time channel layer, job queue/broker needs, and short-lived cache needs.
- Store attachment metadata in PostgreSQL and use a dedicated object/file storage mechanism; the provider is TBD.
- Put AI behind an application service boundary so suggestions are reviewable and approval is recorded. Provider choice is TBD.
- JWT vs. OAuth2 authentication is TBD.

## 11. MVP exclusions

- Jira, Azure DevOps, and other sprint/work-tracking integrations.
- Slack/Microsoft Teams integrations and notifications.
- Multiple or custom retro templates; the MVP uses Start/Stop/Continue.
- Wins and Kudos as separate feedback categories.
- Built-in audio/video recording, media-player, or transcription system.
- AI facilitation, live-discussion interruption, team-health scoring, or autonomous action creation.
- Advanced analytics, advanced reporting, and PDF/Markdown export.
- Mobile app.
- Complex/configurable voting methods beyond three distributable topic votes.
- Automated recurring retros.
- Multiple AI providers as a required feature.
- Organization-wide administration.

## 12. Unresolved decisions / future questions (TBD)

- Target market and primary buyer/user emphasis (general software teams, internal teams, engineering managers, Scrum Masters, or another focus).
- Exact team roles and authorization matrix, including who can view internally retained anonymous-card authors.
- Required retro setup fields, invitation delivery mechanism, and whether pre-meeting feedback preparation is supported.
- Whether submission progress is visible and, if so, to whom and at what level of detail.
- Detailed clustering-board permissions, edit conflict behavior, and facilitator override.
- Whether vote totals remain hidden until voting closes and the exact facilitator selection behavior for discussion topics.
- Discussion comment model, decision record structure, and action ownership rules (including whether a team may be an owner).
- Reopening stages, post-close editing, and retention/deletion policies.
- Attachment storage provider, file constraints, access controls, and retention.
- Authentication choice (JWT, OAuth2, or another approach).
- AI provider, data handling/privacy requirements, prompt/audit strategy, historical-pattern thresholds, and cost controls.
- UI technology, deployment/hosting, observability, backups, and security/compliance requirements.

## 13. Concise next steps

1. Resolve the TBD decisions that affect permissions, invitation/preparation, vote visibility, and stage transitions.
2. Convert this plan into user stories and acceptance criteria for facilitator and participant journeys.
3. Define the Django domain model and state-transition rules.
4. Specify REST endpoints and WebSocket event contracts, including authorization checks.
5. Wireframe the 11 proposed screens and validate the complete facilitator/participant journey.
6. Build the smallest vertical slice: authentication → team → retro → private feedback → simultaneous reveal → clustering → three-vote prioritization → actions → next-retro review.
