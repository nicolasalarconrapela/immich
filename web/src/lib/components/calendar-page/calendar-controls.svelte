<script lang="ts">
  import { Icon } from '@immich/ui';
  import { mdiCheck, mdiChevronDown, mdiChevronLeft, mdiChevronRight } from '@mdi/js';
  import { DateTime } from 'luxon';
  import { t } from 'svelte-i18n';

  type ViewMode = 'day' | 'week' | '2weeks' | 'month' | 'year' | 'agenda';

  interface Props {
    currentDate: DateTime;
    onPrevious: () => void;
    onNext: () => void;
    onToday: () => void;
    onJumpToDate: (date: DateTime) => void;
    viewMode: ViewMode;
  }

  let { currentDate, onPrevious, onNext, onToday, onJumpToDate, viewMode = $bindable() }: Props = $props();

  let showQuickPicker = $state(false);
  let showViewDropdown = $state(false);
  let dateInput: HTMLInputElement;

  // Dynamic Header Title based on View Mode
  const headerTitle = $derived.by(() => {
    const capitalize = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

    switch (viewMode) {
      case 'year': {
        return currentDate.toFormat('yyyy');
      }
      case 'month': {
        return capitalize(currentDate.toFormat("MMMM 'de' yyyy"));
      }
      case 'day': {
        return capitalize(currentDate.toFormat("d 'de' MMMM 'de' yyyy"));
      }
      case 'week': {
        const startOfWeek = currentDate.startOf('week');
        const endOfWeek = currentDate.endOf('week');

        const startMonth = capitalize(startOfWeek.toFormat('MMMM'));
        const endMonth = capitalize(endOfWeek.toFormat('MMMM'));
        const startYear = startOfWeek.toFormat('yyyy');
        const endYear = endOfWeek.toFormat('yyyy');

        if (startYear === endYear) {
          if (startMonth === endMonth) {
            return `${startOfWeek.day} – ${endOfWeek.day} de ${startMonth} de ${startYear}`;
          }
          const startMonthShort = capitalize(startOfWeek.toFormat('MMM'));
          const endMonthShort = capitalize(endOfWeek.toFormat('MMM'));
          return `${startOfWeek.day} ${startMonthShort} – ${endOfWeek.day} ${endMonthShort} de ${startYear}`;
        } else {
          const startMonthShort = capitalize(startOfWeek.toFormat('MMM'));
          const endMonthShort = capitalize(endOfWeek.toFormat('MMM'));
          return `${startOfWeek.day} ${startMonthShort} de ${startYear} – ${endOfWeek.day} ${endMonthShort} de ${endYear}`;
        }
      }
      default: {
        return '';
      }
    }
  });

  // Badge for week number (shown for week and day views)
  const weekBadge = $derived.by(() => {
    if (viewMode === 'week' || viewMode === 'day') {
      return `Semana ${currentDate.weekNumber}`;
    }
    return null;
  });

  // View options for dropdown
  const viewOptions: { value: ViewMode; label: string }[] = [
    { value: 'day', label: 'Día' },
    { value: 'week', label: 'Semana' },
    { value: 'month', label: 'Mes' },
    { value: 'year', label: 'Año' },
  ];

  const monthYear = $derived(currentDate.toFormat('MMMM'));
  const year = $derived(currentDate.year);

  // Month names for picker
  const months = [
    'Enero',
    'Febrero',
    'Marzo',
    'Abril',
    'Mayo',
    'Junio',
    'Julio',
    'Agosto',
    'Septiembre',
    'Octubre',
    'Noviembre',
    'Diciembre',
  ];

  // Generate years range (10 years before and after current year)
  const yearsRange = $derived(() => {
    const years: number[] = [];
    for (let y = year - 10; y <= year + 10; y++) {
      years.push(y);
    }
    return years;
  });

  // Generate days of current month
  const daysInMonth = $derived(() => {
    const start = currentDate.startOf('month');
    const end = currentDate.endOf('month');
    const days: DateTime[] = [];
    let day = start;
    while (day <= end) {
      days.push(day);
      day = day.plus({ days: 1 });
    }
    return days;
  });

  // Generate weeks of current month (for week picker)
  const weeksInMonth = $derived(() => {
    const start = currentDate.startOf('month').startOf('week');
    const end = currentDate.endOf('month').endOf('week');
    const weeks: { start: DateTime; end: DateTime; weekNumber: number }[] = [];
    let weekStart = start;
    while (weekStart <= end) {
      const weekEnd = weekStart.endOf('week');
      weeks.push({
        start: weekStart,
        end: weekEnd,
        weekNumber: weekStart.weekNumber,
      });
      weekStart = weekStart.plus({ weeks: 1 });
    }
    return weeks;
  });

  function selectView(view: ViewMode) {
    viewMode = view;
  }

  function toggleQuickPicker() {
    showQuickPicker = !showQuickPicker;
  }

  function closeQuickPicker() {
    showQuickPicker = false;
  }

  function handleJumpClick() {
    if (dateInput.showPicker) {
      dateInput.showPicker();
    } else {
      dateInput.click();
    }
  }

  function onDatePicked(event: Event) {
    const val = (event.target as HTMLInputElement).value;
    if (val) {
      onJumpToDate(DateTime.fromISO(val));
    }
  }

  function selectMonth(monthIndex: number) {
    const newDate = currentDate.set({ month: monthIndex + 1 });
    onJumpToDate(newDate);
    closeQuickPicker();
  }

  function selectYear(selectedYear: number) {
    const newDate = currentDate.set({ year: selectedYear });
    onJumpToDate(newDate);
    closeQuickPicker();
  }

  function selectDay(day: DateTime) {
    onJumpToDate(day);
    closeQuickPicker();
  }

  function selectWeek(weekStart: DateTime) {
    onJumpToDate(weekStart);
    closeQuickPicker();
  }

  function handleQuickPickerClick(e: MouseEvent) {
    e.stopPropagation();
  }

  function toggleViewDropdown(e: MouseEvent) {
    e.stopPropagation();
    showViewDropdown = !showViewDropdown;
  }

  function closeViewDropdown() {
    showViewDropdown = false;
  }

  function selectViewOption(view: ViewMode) {
    viewMode = view;
    showViewDropdown = false;
  }
</script>

<svelte:window
  onclick={() => {
    closeQuickPicker();
    closeViewDropdown();
  }}
/>

<div class="controls-container">
  <!-- Left Side -->
  <div class="left-group">
    <!-- Today Button -->
    <button type="button" class="today-btn" onclick={onToday}> Hoy </button>

    <!-- Navigation Arrows -->
    <div class="nav-arrows">
      <button type="button" class="nav-btn" onclick={onPrevious} title={$t('previous')}>
        <Icon icon={mdiChevronLeft} size="24" />
      </button>
      <button type="button" class="nav-btn" onclick={onNext} title={$t('next')}>
        <Icon icon={mdiChevronRight} size="24" />
      </button>
    </div>

    <!-- Title & Week Badge -->
    <div class="title-group">
      <span class="header-title">{headerTitle}</span>
      {#if weekBadge}
        <span class="week-badge">{weekBadge}</span>
      {/if}
    </div>
  </div>

  <!-- Right Side: View Dropdown -->
  <div class="right-group">
    <div class="view-dropdown-container">
      <button type="button" class="view-btn" onclick={toggleViewDropdown}>
        <span>{viewOptions.find((v) => v.value === viewMode)?.label}</span>
        <Icon icon={mdiChevronDown} size="18" />
      </button>

      {#if showViewDropdown}
        <!-- svelte-ignore a11y_click_events_have_key_events -->
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div class="dropdown-menu" onclick={(e) => e.stopPropagation()}>
          {#each viewOptions as option (option.value)}
            <button
              type="button"
              class="dropdown-item"
              class:selected={viewMode === option.value}
              onclick={() => selectViewOption(option.value)}
            >
              <span>{option.label}</span>
              {#if viewMode === option.value}
                <Icon icon={mdiCheck} size="16" />
              {/if}
            </button>
          {/each}
        </div>
      {/if}
    </div>
  </div>

  <!-- Hidden Quick Picker (for title click - optional) -->
  <input
    type="date"
    bind:this={dateInput}
    class="hidden-input"
    onchange={onDatePicked}
    onclick={(e) => e.stopPropagation()}
  />
</div>

<style>
  .controls-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    padding: 0.5rem 0;
    --ctrl-bg: #1e293b; /* Slate 800 */
    --ctrl-border: rgba(255, 255, 255, 0.1);
    --ctrl-text: #f8fafc;
    --ctrl-muted: #94a3b8;
    --ctrl-active: #38bdf8;
  }

  /* Left Group */
  .left-group {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .today-btn {
    background: #2a2a2a;
    border: 1px solid var(--ctrl-border);
    color: var(--ctrl-text);
    padding: 0.5rem 1.25rem;
    border-radius: 9999px; /* Pill shape */
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .today-btn:hover {
    background: #3a3a3a;
    border-color: rgba(255, 255, 255, 0.2);
  }

  .nav-arrows {
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }

  .nav-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: none;
    color: var(--ctrl-muted);
    padding: 0.5rem;
    border-radius: 50%;
    cursor: pointer;
    transition: all 0.2s;
  }

  .nav-btn:hover {
    color: var(--ctrl-text);
    background: rgba(255, 255, 255, 0.08);
  }

  .title-group {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .header-title {
    font-size: 1.375rem;
    font-weight: 400;
    color: var(--ctrl-text);
    letter-spacing: -0.01em;
  }

  .week-badge {
    background: #3a3a3a;
    color: var(--ctrl-muted);
    font-size: 0.75rem;
    padding: 0.25rem 0.625rem;
    border-radius: 0.375rem;
    font-weight: 500;
  }

  /* Right Group */
  .right-group {
    display: flex;
    align-items: center;
  }

  .view-dropdown-container {
    position: relative;
  }

  .view-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: #2a2a2a;
    border: 1px solid var(--ctrl-border);
    color: var(--ctrl-text);
    padding: 0.5rem 1rem;
    padding-right: 0.75rem;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    min-width: 110px;
    justify-content: space-between;
  }

  .view-btn:hover {
    background: #3a3a3a;
    border-color: rgba(255, 255, 255, 0.2);
  }

  .dropdown-menu {
    position: absolute;
    top: calc(100% + 0.5rem);
    right: 0;
    background: #1e1e1e;
    border: 1px solid var(--ctrl-border);
    border-radius: 0.75rem;
    padding: 0.375rem;
    min-width: 140px;
    box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.5);
    z-index: 100;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .dropdown-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    padding: 0.5rem 0.75rem;
    background: transparent;
    border: none;
    color: #cbd5e1;
    font-size: 0.875rem;
    cursor: pointer;
    text-align: left;
    border-radius: 0.5rem;
    transition: background 0.2s;
  }

  .dropdown-item:hover {
    background: rgba(255, 255, 255, 0.05);
    color: white;
  }

  .dropdown-item.selected {
    color: var(--ctrl-active);
    font-weight: 600;
    background: rgba(56, 189, 248, 0.1);
  }

  .hidden-input {
    position: absolute;
    width: 0;
    height: 0;
    opacity: 0;
    pointer-events: none;
  }

  @media (max-width: 768px) {
    .controls-container {
      flex-direction: column;
      gap: 1rem;
      align-items: flex-start;
    }

    .left-group {
      flex-wrap: wrap;
      gap: 0.75rem;
    }

    .right-group {
      align-self: flex-end;
    }

    .header-title {
      font-size: 1.125rem;
    }
  }
</style>
