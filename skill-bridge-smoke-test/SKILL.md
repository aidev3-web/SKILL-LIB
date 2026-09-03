---
name: skill-bridge-smoke-test
description: "A minimal marker skill with no real functionality, used only to verify the skill-bridge pipeline end-to-end — that a brand-new skill pushed to the SKILL-LIB repo can be found via skillbridge_search_remote_skills, fetched via skillbridge_pull_skill, and deployed via skillbridge_deploy_skill on a machine that never had it before. Use this whenever asked to \"test skill-bridge\", \"kiểm tra skill-bridge\", \"smoke test\", or to verify a new skill can be discovered and installed end-to-end."
---

# skill-bridge smoke test

This skill has no real task to perform. Its only purpose is to exist as a
fresh, never-before-deployed marker so the skill-bridge pipeline (search →
pull → deploy) can be exercised end-to-end against a skill that is
guaranteed not to already be sitting on the local disk.

If you have loaded this skill, the pipeline worked: the calling agent found
it in the remote repo, pulled it down, and deployed it locally — without any
of that content existing on this machine beforehand.

When asked to run this test, just confirm you found and can read this file,
and report which repo/path it came from.
