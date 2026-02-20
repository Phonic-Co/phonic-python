## 0.31.0 - 2026-02-20
* feat: add audio_url field to Voice model and update Conversation fields
* Add audio_url field to Voice model to support voice sample audio files,
* make started_at field optional in Conversation model for better flexibility,
* and update documentation to clarify presigned URL expiration times.
* Key changes:
* Add audio_url field to Voice model and VoiceParams with 7-day expiration
* Make started_at field optional in Conversation model and ConversationParams
* Update audio_url documentation to specify 1-day expiration for conversations
* Improve API flexibility by allowing conversations without explicit start times
* 🌿 Generated with Fern

