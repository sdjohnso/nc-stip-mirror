# Pull Request Guide for Maintainers

This guide explains how GitHub Pull Requests work and how to handle them for this repository.

---

## What is a Pull Request (PR)?

A Pull Request is when someone:
1. Makes a copy (fork) of your repository
2. Makes changes in their copy
3. Asks you to "pull" their changes into your main repository

It's like someone saying: "Hey, I fixed something / added something. Want to include it?"

---

## How You'll Be Notified

- **Email**: GitHub sends an email to sdjohnso@gmail.com when a PR is opened
- **GitHub UI**: Yellow notification dot on github.com when logged in
- **Subject line**: Usually "[nc-stip-mirror] Pull request #X: Title"

---

## Reviewing a Pull Request

### Step 1: Go to the PR

Click the link in the email, or go to:
`https://github.com/YOUR_USERNAME/nc-stip-mirror/pulls`

### Step 2: Look at What Changed

- **Files changed** tab shows exactly what they modified
- Green lines = additions
- Red lines = deletions
- Review if the changes make sense

### Step 3: Check the Conversation

- Read their description of what they changed and why
- Look for any discussion in the comments

### Step 4: Decide

**If it looks good:**
- Click the green **"Merge pull request"** button
- Click **"Confirm merge"**
- Done! Their changes are now in your repo.

**If you have questions:**
- Leave a comment asking for clarification
- They'll get notified and can respond

**If you don't want the changes:**
- Click **"Close pull request"** (without merging)
- Optionally leave a polite comment explaining why

---

## Types of PRs You Might See

### Good PRs to Accept
- Fixing a typo in documentation
- Correcting a data error they noticed
- Improving the README
- Bug fixes in the scripts
- Adding missing information

### PRs to Be Cautious About
- Major changes to how the scripts work (ask me to review first)
- Changes that add opinion/analysis (this is a mirror, not analysis)
- Changes that would break the automation

### PRs to Decline
- Adding non-NCDOT data sources
- Promotional content or spam
- Changes that violate the "mirror, not transform" philosophy

---

## Quick Reference Commands

If you're ever in the GitHub web interface and confused:

| Want to... | Do this |
|------------|---------|
| See all open PRs | Go to "Pull requests" tab |
| Merge a PR | Green "Merge pull request" button |
| Decline a PR | "Close pull request" button |
| Ask a question | Leave a comment in the PR |
| See what changed | Click "Files changed" tab |

---

## If You're Unsure

Just leave a comment on the PR saying something like:
> "Thanks for the contribution! Let me review this and get back to you."

Then ask me (Claude) to look at it in your next session. I can review the PR and advise whether to merge.

---

## Automated PRs (Dependabot)

GitHub may automatically create PRs to update dependencies (called Dependabot PRs). These are safe to merge if they pass the checks. They'll have titles like:
> "Bump requests from 2.28.0 to 2.31.0"

These keep your dependencies secure and up to date.
