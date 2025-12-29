<script lang="ts">
  import { Icon } from '@immich/ui';
  import { mdiChevronDown, mdiChevronLeft, mdiChevronRight } from '@mdi/js';
  import { DateTime } from 'luxon';
  import { t } from 'svelte-i18n';

  type ViewMode = 'day' | 'week' | '2weeks' | 'month' | 'year' | 'agenda';

  interface ViewOption {
    value: ViewMode;
    label: string;
    shortcut: string;
  }

  interface Props {
    currentDate: DateTime;
    onPrevious: () => void;
    onNext: () => void;
    onToday: () => void;
    viewMode: ViewMode;
  }

  let { currentDate, onPrevious, onNext, onToday, viewMode = $bindable() }: Props = $props();

  let showDropdown = $state(false);

  const viewOptions: ViewOption[] = [
    { value: 'day', label: 'Día', shortcut: 'D' },
    { value: 'week', label: 'Semana', shortcut: 'W' },
    { value: 'month', label: 'Mes', shortcut: 'M' },
    { value: 'year', label: 'Año', shortcut: 'Y' },
    { value: 'agenda', label: 'Agenda', shortcut: 'A' },
    { value: '2weeks', label: '2 semanas', shortcut: 'X' },
  ];

  const currentViewLabel = $derived(viewOptions.find((v) => v.value === viewMode)?.label || 'Mes');

  const monthYear = $derived(currentDate.toFormat('MMMM'));
  const year = $derived(currentDate.year);

  function selectView(view: ViewMode) {
    viewMode = view;
    showDropdown = false;
  }

  function toggleDropdown() {
    showDropdown = !showDropdown;
  }

  function closeDropdown() {
    showDropdown = false;
  }
</script>

<svelte:window on:click={closeDropdown} />

<div class="controls-container">
  <!-- View mode selector -->
  <div class="view-selector-wrapper">
    <button
      type="button"
      class="view-selector"
      onclick={(e) => {
        e.stopPropagation();
        toggleDropdown();
      }}
    >
      <span>{currentViewLabel}</span>
      <Icon icon={mdiChevronDown} size="18" />
    </button>

    {#if showDropdown}
      <div class="dropdown" onclick={(e) => e.stopPropagation()}>
        {#each viewOptions as option}
          <button
            type="button"
            class="dropdown-item"
            class:active={viewMode === option.value}
            onclick={() => selectView(option.value)}
          >
            <span class="item-label">{option.label}</span>
            <span class="item-shortcut">{option.shortcut}</span>
          </button>
        {/each}
      </div>
    {/if}
  </div>

  <!-- Navigation -->
  <div class="nav-buttons">
    <button type="button" class="nav-btn" onclick={onPrevious} title={$t('previous')}>
      <Icon icon={mdiChevronLeft} size="24" />
    </button>

    <button type="button" class="nav-btn" onclick={onNext} title={$t('next')}>
      <Icon icon={mdiChevronRight} size="24" />
    </button>
  </div>

  <!-- Month/Year display -->
  <span class="date-display">
    {monthYear}
    {year}
  </span>

  <!-- Today button -->
  <button type="button" class="today-btn" onclick={onToday} title={$t('today')}>
    <span class="today-number">{DateTime.now().day}</span>
  </button>
</div>

<style>
  .controls-container {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .view-selector-wrapper {
    position: relative;
  }

  .view-selector {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: #2a2a2a;
    border: 1px solid #444;
    color: white;
    font-size: 0.875rem;
    font-weight: 500;
    padding: 0.5rem 1rem;
    border-radius: 2rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .view-selector:hover {
    background: #333;
    border-color: #555;
  }

  .dropdown {
    position: absolute;
    top: calc(100% + 0.5rem);
    left: 0;
    background: #1f1f1f;
    border: 1px solid #333;
    border-radius: 0.75rem;
    min-width: 180px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    z-index: 1000;
    animation: fadeIn 0.15s ease;
    overflow: hidden;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(-8px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .dropdown-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    padding: 0.75rem 1rem;
    background: none;
    border: none;
    color: #e5e5e5;
    font-size: 0.9rem;
    cursor: pointer;
    transition: background 0.15s;
  }

  .dropdown-item:hover {
    background: #2a2a2a;
  }

  .dropdown-item.active {
    color: #4ade80;
  }

  .item-label {
    text-align: left;
  }

  .item-shortcut {
    color: #666;
    font-size: 0.75rem;
    font-weight: 500;
  }

  .nav-buttons {
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }

  .nav-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    background: none;
    border: none;
    color: white;
    padding: 0.5rem;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: background 0.2s;
  }

  .nav-btn:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  .date-display {
    font-size: 1.25rem;
    font-weight: 400;
    color: white;
    text-transform: capitalize;
    min-width: 160px;
  }

  .today-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    background: none;
    border: 2px solid currentColor;
    border-radius: 0.5rem;
    color: white;
    cursor: pointer;
    transition: all 0.2s;
  }

  .today-btn:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  .today-number {
    font-size: 0.875rem;
    font-weight: 600;
  }

  @media (max-width: 640px) {
    .date-display {
      display: none;
    }
  }
</style>
