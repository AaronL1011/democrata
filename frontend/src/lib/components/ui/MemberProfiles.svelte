<script lang="ts">
  import { getPartyColor } from '$lib/constants/partyColors';

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
  let members = $derived(
    ((data.members as MemberProfile[]) || []).filter((m) => m.name)
  );
  let caption = $derived(data.caption as string | undefined);
</script>

{#if members.length > 0}
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
{/if}

<style>
  .member-profiles {
    width: 100%;
  }

  .title {
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
    margin: 0 0 var(--spacing-3);
  }

  .members-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: var(--spacing-4);
  }

  .member-card {
    background: var(--color-surface);
    border-radius: var(--radius-md);
    padding: var(--spacing-4);
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-sm);
    transition: box-shadow var(--transition-base), transform var(--transition-base);
  }

  .member-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
  }

  .member-header {
    display: flex;
    gap: var(--spacing-3);
    align-items: flex-start;
    margin-bottom: var(--spacing-3);
  }

  .member-photo {
    width: 48px;
    height: 48px;
    border-radius: var(--radius-full);
    object-fit: cover;
    flex-shrink: 0;
    border: 2px solid var(--color-border-light);
  }

  .member-photo-placeholder {
    width: 48px;
    height: 48px;
    border-radius: var(--radius-full);
    background: var(--color-gray-200);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: var(--font-weight-semibold);
    color: var(--color-gray-600);
    font-size: var(--font-size-sm);
    flex-shrink: 0;
  }

  .member-info {
    flex: 1;
    min-width: 0;
  }

  .member-name {
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
    margin: 0 0 var(--spacing-1);
  }

  .member-name a {
    color: inherit;
    text-decoration: none;
    transition: color var(--transition-fast);
  }

  .member-name a:hover {
    color: var(--color-primary);
  }

  .party-badge {
    display: inline-block;
    padding: var(--spacing-1) var(--spacing-2);
    border-radius: var(--radius-full);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-medium);
    color: var(--color-text-inverse);
  }

  .constituency {
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
    margin: 0 0 var(--spacing-2);
  }

  .roles {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-2);
    margin-bottom: var(--spacing-2);
  }

  .role-tag {
    display: inline-block;
    padding: var(--spacing-1) var(--spacing-2);
    background: var(--color-gray-100);
    border-radius: var(--radius-sm);
    font-size: var(--font-size-xs);
    color: var(--color-gray-700);
  }

  .biography {
    font-size: var(--font-size-sm);
    color: var(--color-gray-600);
    line-height: var(--line-height-normal);
    margin: 0;
  }

  .caption {
    margin-top: var(--spacing-3);
    font-size: var(--font-size-xs);
    color: var(--color-text-secondary);
    font-style: italic;
  }
</style>
