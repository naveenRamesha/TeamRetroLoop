# TeamRetroLoop MVP backlog

## 1. Bootstrap an empty Django project with a passing test
Goal: Establish a runnable, tested application baseline.
Description: Create the Django project structure, dependency configuration, and a minimal test configuration. Add one smoke test and document the command that runs it so a fresh checkout can demonstrate a passing test suite.

## 2. Add authenticated user accounts and profile access
Goal: Let a person securely identify themselves to the application.
Description: Implement the selected authentication mechanism, login/logout flow, and a basic authenticated-user profile endpoint or page. Add tests for successful authentication, unauthenticated access, and isolation between users.

## 3. Build teams, memberships, and team-manager controls
Goal: Let users collaborate in one or more controlled teams.
Description: Add team and membership models plus UI/API flows to create a team, list a user’s teams, and view its members. Let designated team managers add or remove members, and test that non-members and non-managers cannot access or change another team.

## 4. Create retrospectives and manage their lifecycle
Goal: Give a team a facilitator-led session with an enforceable workflow.
Description: Add retro creation with team, sprint label, scheduled date/time, and facilitator, validating that the facilitator belongs to the team. Model and test the MVP stages—Lobby, Collecting Feedback, Clustering, Voting, Discussion, Summary, and Closed—and let only the facilitator make valid stage transitions.

## 5. Build the dashboard and retro lobby
Goal: Let team members find and enter the retrospectives available to them.
Description: Create a dashboard showing a user’s upcoming and recent team retrospectives, with a route into the selected session. In the lobby, show the sprint, schedule, facilitator, current stage, and eligible members while enforcing team-scoped access.

## 6. Add real-time session presence and stage updates
Goal: Keep authorized participants aware of who is present and where the session is in its flow.
Description: Implement authenticated WebSocket communication scoped to a single retro session. Broadcast participant presence and facilitator stage changes, and cover unauthorized connection attempts with automated tests.

## 7. Implement private Start, Stop, and Continue feedback collection
Goal: Enable participants to submit candid feedback before it is shared.
Description: Add creation, editing, listing, and deletion of feedback cards in the fixed Start, Stop, and Continue categories, including an anonymous-attribution option per card. During the Collecting Feedback stage, expose only the submitting participant’s cards and ensure anonymous cards never reveal their author in public representations.

## 8. Reveal feedback simultaneously and show the shared board
Goal: Make all submitted feedback available to the team at one explicit moment.
Description: Add a facilitator-only reveal action that moves the session from private collection into the clustering stage and notifies participants in real time. Build the shared board that displays revealed cards by category, honoring each card’s anonymous-attribution setting.

## 9. Add collaborative topic clustering
Goal: Let the team group related revealed cards into discussion topics.
Description: Add discussion topics and let authorized participants create, rename, delete, and assign or move revealed cards between topics on the shared board. Persist each change and broadcast it to the session, with safe handling for stale edits so a card assignment is not silently overwritten.

## 10. Implement topic voting and prioritization
Goal: Let each participant allocate exactly three votes to the topics worth discussing.
Description: Add a voting board and server-side vote records that allow a participant to distribute up to three votes across topics, including multiple votes on one topic. Show ranked totals to authorized session members and prevent voting outside the Voting stage or above the allowed total.

## 11. Build the facilitated discussion workspace
Goal: Capture the team’s discussion of prioritized topics.
Description: Let the facilitator select a topic for discussion and provide a shared area for discussion notes and participant comments. Persist the notes and comments against the topic, synchronize appropriate updates in real time, and allow the facilitator to mark a topic as discussed.

## 12. Record decisions and action items from a discussion
Goal: Preserve outcomes and accountable follow-up work separately.
Description: Let participants record decisions linked to the retro and optional discussion topic, without automatically creating an action. Add action items with title, description, owner, due date, priority, status, and links to their originating retro/topic; allow authorized updates through Open, In Progress, Completed, and Cancelled.

## 13. Add action tracking and next-retro review
Goal: Ensure a team can follow through on commitments between retrospectives.
Description: Build a team-scoped action list that shows owner, due date, priority, status, and derived Not Started or Overdue states. When a new retro opens, display prior team actions and allow the team to record whether an action helped.

## 14. Produce a final summary and retrospective history
Goal: Leave each closed retro with an accessible record of its outcomes.
Description: Create a facilitator-editable summary containing discussed topics, decisions, and action items, then provide an authorized close operation. Build a team history view for closed retros that opens its summary and recorded outcomes while preventing access by non-members.

## 15. Add MVP-wide authorization and workflow regression tests
Goal: Prevent privacy and workflow regressions in the completed MVP.
Description: Add focused end-to-end or integration coverage for team isolation, facilitator-only controls, pre-reveal feedback privacy, anonymous-card attribution, voting limits, and closed-retro access. Use the tests to verify the main facilitator and participant journeys from login through summary.
