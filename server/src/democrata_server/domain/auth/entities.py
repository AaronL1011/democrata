@dataclass
class User:
    id: UUID
    email: str
    name: str | None
    avatar_url: str | None
    email_verified: bool
    created_at: datetime
    updated_at: datetime

@dataclass
class Organization:
    id: UUID
    name: str
    slug: str  # URL-friendly identifier
    owner_id: UUID
    billing_email: str
    plan: OrganizationPlan  # free | pro | enterprise
    max_seats: int
    created_at: datetime

@dataclass
class Membership:
    id: UUID
    user_id: UUID
    organization_id: UUID
    role: MemberRole  # owner | admin | member | viewer
    invited_by: UUID | None
    joined_at: datetime