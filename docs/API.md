# API Reference

Base URL: `/api/v1`
All responses: `{ success: bool, data: T, error: string | null }`

## Authentication
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | /auth/register | Register with email/password | Public |
| POST | /auth/login | Login with email/password | Public |
| POST | /auth/google | Google OAuth callback | Public |
| POST | /auth/refresh | Refresh JWT token | Authenticated |

## Users
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | /users/me | Get current user + profile | Authenticated |
| PUT | /users/me/profile | Update profile | Student |

## Dashboard
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | /dashboard | Full dashboard data | Student |

## Experiences
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | /experiences | Submit new experience | Student |
| GET | /experiences?page&limit | List experiences (paginated) | Student |
| GET | /experiences/:id | Get experience detail | Student |
| PUT | /experiences/:id | Update experience | Owner/Admin |
| DELETE | /experiences/:id | Delete experience | Owner/Admin |

## Companies
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | /companies?search | List companies with stats | Student |
| GET | /companies/:id | Full company intelligence | Student |
| POST | /companies | Create company | Admin |
| PUT | /companies/:id | Update company | Admin |

## Mock Interviews
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | /interviews/start | Start new mock interview | Student |
| POST | /interviews/:id/answer | Submit answer + get next Q | Student |
| POST | /interviews/:id/complete | End interview + get eval | Student |
| GET | /interviews | List past interviews | Student |
| GET | /interviews/:id | Get interview detail | Student |
| GET | /interviews/:id/replay | Get full replay data | Student |

## Resume
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | /resume/upload | Upload resume (PDF/text) | Student |
| GET | /resume/insights | Get resume insights | Student |

## Intelligence
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | /weaknesses | Get user's weaknesses | Student |
| PUT | /weaknesses/:id/resolve | Mark weakness resolved | Student |
| GET | /recommendations | Get personalized recommendations | Student |
| PUT | /recommendations/:id/complete | Mark recommendation done | Student |
| GET | /readiness | Overall readiness | Student |
| GET | /readiness/:company_id | Company-specific readiness | Student |
| GET | /search?q&type&company | Search knowledge base | Student |

## Voice
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | /voice/transcribe | Speech to text | Student |
| POST | /voice/synthesize | Text to speech | Student |

## Admin
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | /admin/experiences?status | List experiences for moderation | Admin |
| PUT | /admin/experiences/:id/approve | Approve experience | Admin |
| PUT | /admin/experiences/:id/flag | Flag experience | Admin |
| GET | /admin/analytics | Platform analytics | Admin |
