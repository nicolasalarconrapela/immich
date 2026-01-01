<script lang="ts">
  import { Icon } from '@immich/ui';
  import { mdiCalendar, mdiChevronLeft, mdiChevronRight, mdiClose } from '@mdi/js';
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

  let showDropdown = $state(false);
  let showQuickPicker = $state(false);
  let dateInput: HTMLInputElement;

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
    showDropdown = false;
  }

  function closeDropdown() {
    showDropdown = false;
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
</script>

<svelte:window onclick={closeQuickPicker} />

<div class="controls-container">
  <!-- Navigation -->
  <div class="nav-buttons">
    <button type="button" class="nav-btn" onclick={onPrevious} title={$t('previous')}>
      <Icon icon={mdiChevronLeft} size="24" />
    </button>

    <button type="button" class="nav-btn" onclick={onNext} title={$t('next')}>
      <Icon icon={mdiChevronRight} size="24" />
    </button>
  </div>

  <!-- Date Controls (Pill: Today | Quick Pick) -->
  <div class="date-controls">
    <button type="button" class="date-btn" onclick={onToday}>Today</button>
    <div class="separator"></div>
    <button
      type="button"
      class="date-btn icon-text"
      onclick={(e) => {
        e.stopPropagation();
        toggleQuickPicker();
      }}
    >
      <Icon icon={mdiCalendar} size="16" />
      <span>{monthYear} {year}</span>
    </button>

    <!-- Hidden Native Date Input (fallback) -->
    <input
      type="date"
      bind:this={dateInput}
      class="hidden-input"
      onchange={onDatePicked}
      onclick={(e) => e.stopPropagation()}
    />

    <!-- Quick Picker Dropdown -->
    {#if showQuickPicker}
      <!-- svelte-ignore a11y_click_events_have_key_events -->
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <div class="quick-picker" onclick={handleQuickPickerClick}>
        <div class="picker-header">
          <span class="picker-title">
            {#if viewMode === 'year'}
              Seleccionar año
            {:else if viewMode === 'month'}
              Seleccionar mes
            {:else if viewMode === 'week'}
              Seleccionar semana
            {:else}
              Seleccionar día
            {/if}
          </span>
          <button type="button" class="picker-close" onclick={closeQuickPicker}>
            <Icon icon={mdiClose} size="18" />
          </button>
        </div>

        <div class="picker-content">
          {#if viewMode === 'year'}
            <!-- Year Picker -->
            <div class="year-grid">
              {#each yearsRange() as y (y)}
                <button type="button" class="picker-item" class:active={y === year} onclick={() => selectYear(y)}>
                  {y}
                </button>
              {/each}
            </div>
          {:else if viewMode === 'month'}
            <!-- Month Picker -->
            <div class="month-grid">
              {#each months as m, index (index)}
                <button
                  type="button"
                  class="picker-item"
                  class:active={index + 1 === currentDate.month}
                  onclick={() => selectMonth(index)}
                >
                  {m}
                </button>
              {/each}
            </div>
          {:else if viewMode === 'week'}
            <!-- Week Picker -->
            <div class="week-list">
              {#each weeksInMonth() as week (week.weekNumber)}
                <button
                  type="button"
                  class="picker-item week-item"
                  class:active={week.weekNumber === currentDate.weekNumber}
                  onclick={() => selectWeek(week.start)}
                >
                  <span class="week-number">S{week.weekNumber}</span>
                  <span class="week-range">
                    {week.start.toFormat('d MMM')} - {week.end.toFormat('d MMM')}
                  </span>
                </button>
              {/each}
            </div>
          {:else}
            <!-- Day Picker (Mini Calendar) -->
            <div class="day-picker">
              <div class="day-header">
                {#each ['L', 'M', 'X', 'J', 'V', 'S', 'D'] as dayName}
                  <span class="day-name">{dayName}</span>
                {/each}
              </div>
              <div class="day-grid">
                {#each daysInMonth() as day (day.toISODate())}
                  <button
                    type="button"
                    class="picker-item day-item"
                    class:active={day.hasSame(currentDate, 'day')}
                    class:today={day.hasSame(DateTime.now(), 'day')}
                    onclick={() => selectDay(day)}
                  >
                    {day.day}
                  </button>
                {/each}
              </div>
            </div>
          {/if}
        </div>

        <!-- Fallback: Open full date picker -->
        <button type="button" class="picker-fallback" onclick={handleJumpClick}>
          <Icon icon={mdiCalendar} size="14" />
          Seleccionar fecha exacta...
        </button>
      </div>
    {/if}
  </div>

  <!-- View Switcher (Tab Style) -->
  <div class="view-switcher">
    <button type="button" class="segment-btn" class:active={viewMode === 'year'} onclick={() => selectView('year')}>
      Año
    </button>
    <button type="button" class="segment-btn" class:active={viewMode === 'month'} onclick={() => selectView('month')}>
      Mes
    </button>
    <button type="button" class="segment-btn" class:active={viewMode === 'week'} onclick={() => selectView('week')}>
      Semana
    </button>
    <button type="button" class="segment-btn" class:active={viewMode === 'day'} onclick={() => selectView('day')}>
      Día
    </button>
  </div>
</div>

<style>
  .controls-container {
    display: flex;
    align-items: center;
    gap: 1rem;
    width: 100%;
    justify-content: space-between;
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

  /* Date Controls Pill */
  .date-controls {
    display: flex;
    align-items: center;
    background: #2a2a2a;
    border: 1px solid #444;
    border-radius: 0.75rem;
    padding: 0.25rem;
    position: relative;
    min-height: 38px;
  }

  .date-btn {
    background: transparent;
    border: none;
    color: #e5e5e5;
    font-size: 0.875rem;
    font-weight: 600;
    padding: 0.25rem 0.75rem;
    cursor: pointer;
    transition: color 0.2s;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .date-btn:hover {
    color: white;
  }

  .icon-text {
    text-transform: capitalize;
  }

  .separator {
    width: 1px;
    height: 16px;
    background: rgba(255, 255, 255, 0.2);
  }

  .hidden-input {
    position: absolute;
    top: 0;
    left: 0;
    width: 0;
    height: 0;
    opacity: 0;
    pointer-events: none;
  }

  /* Quick Picker Dropdown */
  .quick-picker {
    position: absolute;
    top: calc(100% + 8px);
    left: 0;
    min-width: 280px;
    background: #1e1e1e;
    border: 1px solid #444;
    border-radius: 0.75rem;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
    z-index: 100;
    overflow: hidden;
  }

  .picker-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #333;
    background: #252525;
  }

  .picker-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: #e5e5e5;
  }

  .picker-close {
    background: none;
    border: none;
    color: #888;
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 0.25rem;
    display: flex;
  }

  .picker-close:hover {
    color: white;
    background: rgba(255, 255, 255, 0.1);
  }

  .picker-content {
    padding: 0.75rem;
    max-height: 300px;
    overflow-y: auto;
  }

  /* Month Grid */
  .month-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.5rem;
  }

  /* Year Grid */
  .year-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.5rem;
  }

  /* Week List */
  .week-list {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .week-item {
    justify-content: flex-start;
    gap: 1rem;
  }

  .week-number {
    font-weight: 700;
    color: #38bdf8;
    min-width: 2rem;
  }

  .week-range {
    font-size: 0.75rem;
    color: #888;
  }

  /* Day Picker */
  .day-picker {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .day-header {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 0.25rem;
    text-align: center;
  }

  .day-name {
    font-size: 0.75rem;
    font-weight: 600;
    color: #666;
    padding: 0.25rem;
  }

  .day-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 0.25rem;
  }

  .day-item {
    aspect-ratio: 1;
    padding: 0.25rem;
    font-size: 0.75rem;
  }

  .day-item.today {
    border: 1px solid #38bdf8;
  }

  /* Picker Items */
  .picker-item {
    background: rgba(255, 255, 255, 0.05);
    border: none;
    color: #ccc;
    padding: 0.5rem;
    border-radius: 0.5rem;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .picker-item:hover {
    background: rgba(255, 255, 255, 0.1);
    color: white;
  }

  .picker-item.active {
    background: #4ade80;
    color: black;
    font-weight: 600;
  }

  .picker-fallback {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    width: 100%;
    padding: 0.75rem;
    background: none;
    border: none;
    border-top: 1px solid #333;
    color: #888;
    font-size: 0.75rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .picker-fallback:hover {
    background: rgba(255, 255, 255, 0.05);
    color: white;
  }

  /* Segmented Control (Tabs) */
  .view-switcher {
    display: flex;
    background: #2a2a2a;
    border: 1px solid #444;
    border-radius: 0.75rem;
    padding: 4px;
    gap: 4px;
    margin-left: auto;
  }

  .segment-btn {
    background: transparent;
    border: none;
    color: #9ca3af;
    padding: 0.35rem 1rem;
    border-radius: 0.5rem;
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .segment-btn:hover {
    color: white;
  }

  .segment-btn.active {
    background: #4ade80;
    color: #000;
    font-weight: 700;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  }

  @media (max-width: 640px) {
    .date-controls {
      display: none;
    }
  }
</style>
