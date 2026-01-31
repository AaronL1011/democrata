<script lang="ts">
  interface PartyVote {
    party: string;
    votes_for: number;
    votes_against: number;
    abstentions?: number;
    not_voting?: number;
  }

  interface Props {
    data: Record<string, unknown>;
  }

  let { data }: Props = $props();

  let title = $derived(data.title as string | undefined);
  let date = $derived(data.date as string | undefined);
  let result = $derived(data.result as string | undefined);
  let totalFor = $derived((data.total_for as number) || 0);
  let totalAgainst = $derived((data.total_against as number) || 0);
  let totalAbstentions = $derived((data.total_abstentions as number) || 0);
  let partyBreakdown = $derived((data.party_breakdown as PartyVote[]) || []);
  let caption = $derived(data.caption as string | undefined);

  let totalVotes = $derived(totalFor + totalAgainst);
  let forPercent = $derived(totalVotes > 0 ? (totalFor / totalVotes) * 100 : 50);

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
      'Crossbench': '#8b5cf6',
    };
    return partyColors[party] || '#6b7280';
  }
</script>

<div class="voting-breakdown">
  {#if title}
    <div class="header">
      <h3 class="title">{title}</h3>
      {#if result}
        <span class="result-badge" class:passed={result === 'passed'} class:rejected={result === 'rejected'}>
          {result.charAt(0).toUpperCase() + result.slice(1)}
        </span>
      {/if}
    </div>
  {/if}

  {#if date}
    <p class="date">{date}</p>
  {/if}

  <div class="summary">
    <div class="vote-bar">
      <div class="for-bar" style:width="{forPercent}%"></div>
      <div class="against-bar" style:width="{100 - forPercent}%"></div>
    </div>
    <div class="vote-labels">
      <span class="for-label">
        <span class="vote-count">{totalFor}</span> For
      </span>
      {#if totalAbstentions > 0}
        <span class="abstain-label">
          <span class="vote-count">{totalAbstentions}</span> Abstained
        </span>
      {/if}
      <span class="against-label">
        <span class="vote-count">{totalAgainst}</span> Against
      </span>
    </div>
  </div>

  {#if partyBreakdown.length > 0}
    <div class="party-breakdown">
      <h4 class="breakdown-title">By Party</h4>
      <div class="party-list">
        {#each partyBreakdown as party}
          <div class="party-row">
            <div class="party-name">
              <span class="party-dot" style:background-color={getPartyColor(party.party)}></span>
              {party.party}
            </div>
            <div class="party-votes">
              <span class="party-for">{party.votes_for}</span>
              <span class="party-separator">-</span>
              <span class="party-against">{party.votes_against}</span>
              {#if party.abstentions && party.abstentions > 0}
                <span class="party-abstentions">({party.abstentions} abs)</span>
              {/if}
            </div>
          </div>
        {/each}
      </div>
    </div>
  {/if}

  {#if caption}
    <p class="caption">{caption}</p>
  {/if}
</div>

<style>
  .voting-breakdown {
    width: 100%;
  }

  .header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.25rem;
  }

  .title {
    font-size: 1rem;
    font-weight: 600;
    color: #1f2937;
    margin: 0;
  }

  .result-badge {
    padding: 0.125rem 0.625rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.025em;
  }

  .result-badge.passed {
    background: #d1fae5;
    color: #065f46;
  }

  .result-badge.rejected {
    background: #fee2e2;
    color: #991b1b;
  }

  .date {
    font-size: 0.8125rem;
    color: #6b7280;
    margin: 0 0 1rem;
  }

  .summary {
    margin-bottom: 1.25rem;
  }

  .vote-bar {
    display: flex;
    height: 2rem;
    border-radius: 0.375rem;
    overflow: hidden;
    background: #e5e7eb;
  }

  .for-bar {
    background: #22c55e;
    transition: width 0.3s ease;
  }

  .against-bar {
    background: #ef4444;
    transition: width 0.3s ease;
  }

  .vote-labels {
    display: flex;
    justify-content: space-between;
    margin-top: 0.5rem;
    font-size: 0.875rem;
  }

  .for-label {
    color: #16a34a;
  }

  .abstain-label {
    color: #6b7280;
  }

  .against-label {
    color: #dc2626;
  }

  .vote-count {
    font-weight: 700;
  }

  .party-breakdown {
    background: #f9fafb;
    border-radius: 0.5rem;
    padding: 1rem;
  }

  .breakdown-title {
    font-size: 0.8125rem;
    font-weight: 600;
    color: #374151;
    margin: 0 0 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .party-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .party-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.375rem 0;
    border-bottom: 1px solid #e5e7eb;
  }

  .party-row:last-child {
    border-bottom: none;
  }

  .party-name {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    color: #1f2937;
  }

  .party-dot {
    width: 0.625rem;
    height: 0.625rem;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .party-votes {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    font-size: 0.875rem;
  }

  .party-for {
    color: #16a34a;
    font-weight: 600;
    min-width: 2rem;
    text-align: right;
  }

  .party-separator {
    color: #9ca3af;
  }

  .party-against {
    color: #dc2626;
    font-weight: 600;
    min-width: 2rem;
    text-align: left;
  }

  .party-abstentions {
    color: #6b7280;
    font-size: 0.75rem;
    margin-left: 0.25rem;
  }

  .caption {
    margin-top: 0.75rem;
    font-size: 0.75rem;
    color: #6b7280;
    font-style: italic;
  }
</style>
