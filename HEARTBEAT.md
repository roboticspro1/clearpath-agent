## Scheduled Tasks

Every 60 minutes:
- Check for any CASE FILE with status READY FOR REVIEW older than 3 hours with no caseworker response.
- Send a reminder to the caseworker that a case is waiting.

Every 24 hours:
- Check for any case older than 24 hours with no action taken.
- Draft an MOM escalation letter for that case automatically.
- Notify caseworker: "This case has not been acted on in 24 hours. Draft escalation ready — approve to send."