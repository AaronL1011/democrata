<script lang="ts">
  import { getPartyColor } from '$lib/constants/partyColors';

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
              <span class="party-separator">–</span>
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
    gap: var(--spacing-3);
    margin-bottom: var(--spacing-1);
  }

  .title {
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
    margin: 0;
  }

  .result-badge {
    padding: var(--spacing-1) var(--spacing-3);
    border-radius: var(--radius-full);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-semibold);
    text-transform: uppercase;
    letter-spacing: 0.025em;
  }

  .result-badge.passed {
    background: var(--color-success-light);
    color: var(--color-success-text);
  }

  .result-badge.rejected {
    background: var(--color-error-muted);
    color: var(--color-error-text);
  }

  .date {
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
    margin: 0 0 var(--spacing-4);
  }

  .summary {
    margin-bottom: var(--spacing-5);
  }

  .vote-bar {
    display: flex;
    height: 2rem;
    border-radius: var(--radius-sm);
    overflow: hidden;
    background: var(--color-border);
    box-shadow: inset 0 1px 2px rgb(0 0 0 / 0.05);
  }

  .for-bar {
    background: var(--color-vote-for);
    transition: width var(--transition-slow);
  }

  .against-bar {
    background: var(--color-vote-against);
    transition: width var(--transition-slow);
  }

  .vote-labels {
    display: flex;
    justify-content: space-between;
    margin-top: var(--spacing-2);
    font-size: var(--font-size-sm);
  }

  .for-label {
    color: var(--color-vote-for-text);
  }

  .abstain-label {
    color: var(--color-text-secondary);
  }

  .against-label {
    color: var(--color-vote-against-text);
  }

  .vote-count {
    font-weight: var(--font-weight-bold);
  }

  .party-breakdown {
    background: var(--color-gray-50);
    border-radius: var(--radius-md);
    padding: var(--spacing-4);
    border: 1px solid var(--color-border-light);
  }

  .breakdown-title {
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-semibold);
    color: var(--color-gray-700);
    margin: 0 0 var(--spacing-3);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .party-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-2);
  }

  .party-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-2) 0;
    border-bottom: 1px solid var(--color-border-light);
    transition: background-color var(--transition-fast);
  }

  .party-row:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }

  .party-row:first-child {
    padding-top: 0;
  }

  .party-name {
    display: flex;
    align-items: center;
    gap: var(--spacing-2);
    font-size: var(--font-size-sm);
    color: var(--color-text-primary);
  }

  .party-dot {
    width: 0.625rem;
    height: 0.625rem;
    border-radius: var(--radius-full);
    flex-shrink: 0;
    box-shadow: 0 0 0 2px rgb(255 255 255 / 0.8);
  }

  .party-votes {
    display: flex;
    align-items: center;
    gap: var(--spacing-2);
    font-size: var(--font-size-sm);
  }

  .party-for {
    color: var(--color-vote-for-text);
    font-weight: var(--font-weight-semibold);
    min-width: 2rem;
    text-align: right;
  }

  .party-separator {
    color: var(--color-text-muted);
  }

  .party-against {
    color: var(--color-vote-against-text);
    font-weight: var(--font-weight-semibold);
    min-width: 2rem;
    text-align: left;
  }

  .party-abstentions {
    color: var(--color-text-secondary);
    font-size: var(--font-size-xs);
    margin-left: var(--spacing-1);
  }

  .caption {
    margin-top: var(--spacing-3);
    font-size: var(--font-size-xs);
    color: var(--color-text-secondary);
    font-style: italic;
  }
</style>
