<script lang="ts">
  interface MemberProfile {
    member_id: string;
    name: string;
    party: string;
    constituency?: string;
    roles?: string[];
    photo_url?: string;
    biography?: string;
    profile_url?: string;
  }

  interface Props {
    data: Record<string, unknown>;
  }

  let { data }: Props = $props();

  let title = $derived(data.title as string | undefined);
  let members = $derived((data.members as MemberProfile[]) || []);
  let caption = $derived(data.caption as string | undefined);

  function getPartyColor(party: string): string {
    const partyColors: Record<string, string> = {
      'Labour': '#dc2626',
      'Conservative': '#2563eb',
      'Liberal Democrat': '#f97316',
      'Liberal Democrats': '#f97316',
      'SNP': '#fbbf24',
      'Scottish National Party': '#fbbf24',
      'Green': '#16a34a',
      'Green Party': '#16a34a',
      'Plaid Cymru': '#10b981',
      'DUP': '#991b1b',
      'Sinn Féin': '#15803d',
      'SDLP': '#22c55e',
      'Alliance': '#eab308',
      'Independent': '#6b7280',
    };
    return partyColors[party] || '#6b7280';
  }
</script>

<div class="member-profiles">
  {#if title}
    <h3 class="title">{title}</h3>
  {/if}

  <div class="members-grid">
    {#each members as member}
      <div class="member-card">
        <div class="member-header">
          {#if member.photo_url}
            <img src={member.photo_url} alt={member.name} class="member-photo" />
          {:else}
            <div class="member-photo-placeholder">
              {member.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
            </div>
          {/if}
          <div class="member-info">
            <h4 class="member-name">
              {#if member.profile_url}
                <a href={member.profile_url} target="_blank" rel="noopener noreferrer">
                  {member.name}
                </a>
              {:else}
                {member.name}
              {/if}
            </h4>
            <span
              class="party-badge"
              style:background-color={getPartyColor(member.party)}
            >
              {member.party}
            </span>
          </div>
        </div>

        {#if member.constituency}
          <p class="constituency">{member.constituency}</p>
        {/if}

        {#if member.roles && member.roles.length > 0}
          <div class="roles">
            {#each member.roles as role}
              <span class="role-tag">{role}</span>
            {/each}
          </div>
        {/if}

        {#if member.biography}
          <p class="biography">{member.biography}</p>
        {/if}
      </div>
    {/each}
  </div>

  {#if caption}
    <p class="caption">{caption}</p>
  {/if}
</div>

<style>
  .member-profiles {
    width: 100%;
  }

  .title {
    font-size: 1rem;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 0.75rem;
  }

  .members-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
  }

  .member-card {
    background: #f9fafb;
    border-radius: 0.5rem;
    padding: 1rem;
    border: 1px solid #e5e7eb;
  }

  .member-header {
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
    margin-bottom: 0.75rem;
  }

  .member-photo {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    object-fit: cover;
    flex-shrink: 0;
  }

  .member-photo-placeholder {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: #d1d5db;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    color: #4b5563;
    font-size: 0.875rem;
    flex-shrink: 0;
  }

  .member-info {
    flex: 1;
    min-width: 0;
  }

  .member-name {
    font-size: 0.9375rem;
    font-weight: 600;
    color: #1f2937;
    margin: 0 0 0.25rem;
  }

  .member-name a {
    color: inherit;
    text-decoration: none;
  }

  .member-name a:hover {
    color: #2563eb;
    text-decoration: underline;
  }

  .party-badge {
    display: inline-block;
    padding: 0.125rem 0.5rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 500;
    color: white;
  }

  .constituency {
    font-size: 0.8125rem;
    color: #6b7280;
    margin: 0 0 0.5rem;
  }

  .roles {
    display: flex;
    flex-wrap: wrap;
    gap: 0.375rem;
    margin-bottom: 0.5rem;
  }

  .role-tag {
    display: inline-block;
    padding: 0.125rem 0.5rem;
    background: #e5e7eb;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    color: #374151;
  }

  .biography {
    font-size: 0.8125rem;
    color: #4b5563;
    line-height: 1.5;
    margin: 0;
  }

  .caption {
    margin-top: 0.75rem;
    font-size: 0.75rem;
    color: #6b7280;
    font-style: italic;
  }
</style>
