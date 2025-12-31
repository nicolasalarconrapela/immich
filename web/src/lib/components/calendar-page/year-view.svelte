<script lang="ts">
  import { AssetMediaSize, searchAssets, type AssetResponseDto } from '@immich/sdk';
  import { Icon } from '@immich/ui';
  import { mdiCalendarBlank, mdiChevronLeft, mdiChevronRight, mdiImageMultiple } from '@mdi/js';
  import { DateTime } from 'luxon';

  interface Props {
    currentDate: DateTime;
    onNavigate: (direction: number) => void;
    onMonthSelect: (date: DateTime) => void;
    onDaySelect: (date: DateTime) => void;
  }

  let { currentDate, onNavigate, onMonthSelect, onDaySelect }: Props = $props();

  interface MonthHighlight {
    monthIndex: number; // 1-12
    name: string;
    totalCount: number;
    coverAssets: AssetResponseDto[];
    topDays: Array<{
      date: DateTime;
      count: number;
      title: string;
      subtitle: string;
    }>;
  }

  let yearData = $state<MonthHighlight[]>([]);
  let isLoading = $state(true);

  const year = $derived(currentDate.year);

  // Initialize empty months structure
  function getEmptyMonths(): MonthHighlight[] {
    const months: MonthHighlight[] = [];
    for (let m = 1; m <= 12; m++) {
      months.push({
        monthIndex: m,
        name: DateTime.fromObject({ month: m }).toFormat('MMMM'),
        totalCount: 0,
        coverAssets: [],
        topDays: [],
      });
    }
    return months;
  }

  async function loadAssets() {
    isLoading = true;
    yearData = getEmptyMonths();

    try {
      const promises = [];

      for (let m = 1; m <= 12; m++) {
        const monthDate = DateTime.fromObject({ year: currentDate.year, month: m });
        const startOfMonth = monthDate.startOf('month');
        const endOfMonth = monthDate.endOf('month');

        promises.push(
          searchAssets({
            metadataSearchDto: {
              takenAfter: startOfMonth.toISO() ?? undefined,
              takenBefore: endOfMonth.toISO() ?? undefined,
              size: 50,
              withExif: false,
            },
          }).then((result) => ({
            monthIndex: m,
            name: monthDate.toFormat('MMMM'),
            // @ts-ignore
            totalCount: result.assets.total ?? result.assets.items.length,
            items: result.assets.items,
          })),
        );
      }

      const results = await Promise.all(promises);

      yearData = results.map((data) => {
        const mAssets = data.items;
        const coverAssets = mAssets.slice(0, 3);
        const daysInMonth = new Map<string, number>();

        mAssets.forEach((a) => {
          const dKey = DateTime.fromISO(a.fileCreatedAt).toISODate();
          if (dKey) daysInMonth.set(dKey, (daysInMonth.get(dKey) || 0) + 1);
        });

        const sortedDays = [...daysInMonth.entries()].sort((a, b) => b[1] - a[1]).slice(0, 2);

        const topDays = sortedDays.map(([dKey, count]) => {
          const date = DateTime.fromISO(dKey);
          return {
            date,
            count,
            title: `Memories from ${date.toFormat('MMM d')}`,
            subtitle: `Highlights`,
          };
        });

        return {
          monthIndex: data.monthIndex,
          name: data.name,
          totalCount: data.totalCount,
          coverAssets,
          topDays,
        };
      });
    } catch (error) {
      console.error('Failed to load year assets:', error);
    } finally {
      isLoading = false;
    }
  }

  function getThumbnailUrl(asset: AssetResponseDto) {
    return `/api/assets/${asset.id}/thumbnail?size=${AssetMediaSize.Thumbnail}`;
  }

  const totalYearPhotos = $derived(yearData.reduce((acc, m) => acc + m.totalCount, 0));
  const totalYearEvents = $derived(yearData.reduce((acc, m) => acc + m.topDays.length, 0));

  $effect(() => {
    currentDate;
    loadAssets();
  });
</script>

<div class="year-view-container">
  <!-- Summary Header -->
  <header class="summary-header">
    <div class="summary-top">
      <div>
        <h1 class="summary-title">{year} Summary</h1>
        <p class="summary-subtitle">Year in Review</p>
      </div>

      <div class="header-actions">
        <!-- Navigation -->
        <div class="nav-controls">
          <button class="icon-btn" onclick={() => onNavigate(-1)} aria-label="Previous Year">
            <Icon icon={mdiChevronLeft} size="24" />
          </button>
          <button class="icon-btn" onclick={() => onNavigate(1)} aria-label="Next Year">
            <Icon icon={mdiChevronRight} size="24" />
          </button>
        </div>
      </div>
    </div>

    <div class="stats-row">
      <div class="stat-card">
        <span class="stat-value">{isLoading ? '-' : totalYearPhotos.toLocaleString()}</span>
        <span class="stat-label">PHOTOS</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{isLoading ? '-' : totalYearEvents.toLocaleString()}</span>
        <span class="stat-label">EVENTS</span>
      </div>
    </div>
  </header>

  <!-- Grid -->
  <div class="cards-grid">
    {#each yearData as month}
      <div class="month-card">
        <!-- Cover Area -->
        <button
          class="card-header"
          onclick={() => onMonthSelect(DateTime.fromObject({ year, month: month.monthIndex }))}
          type="button"
        >
          {#if month.coverAssets.length > 0}
            <!-- Photo Collage -->
            <div class="collage" class:multi={month.coverAssets.length >= 3}>
              {#if month.coverAssets.length >= 3}
                <div class="collage-main">
                  <img src={getThumbnailUrl(month.coverAssets[0])} alt="" loading="lazy" />
                </div>
                <div class="collage-side">
                  <div class="collage-top">
                    <img src={getThumbnailUrl(month.coverAssets[1])} alt="" loading="lazy" />
                  </div>
                  <div class="collage-bottom">
                    <img src={getThumbnailUrl(month.coverAssets[2])} alt="" loading="lazy" />
                  </div>
                </div>
              {:else}
                <!-- Single Cover -->
                <img src={getThumbnailUrl(month.coverAssets[0])} class="single-cover" alt="" loading="lazy" />
              {/if}

              <!-- Gradient Overlay -->
              <div class="cover-overlay"></div>
            </div>
          {:else}
            <!-- Empty State -->
            <div class="empty-cover">
              <Icon icon={mdiImageMultiple} size="48" class="opacity-20" />
            </div>
          {/if}

          <!-- Month Title Overlay -->
          <div class="header-content">
            <h2 class="month-name">{month.name}</h2>
          </div>

          <!-- Count Badge -->
          {#if month.totalCount > 0}
            <div class="count-badge">
              {month.totalCount} Photos
            </div>
          {/if}
        </button>

        <!-- Events List -->
        <div class="events-list">
          {#each month.topDays as day}
            <button class="event-item" onclick={() => onDaySelect(day.date)} type="button">
              <div class="date-box">
                <span class="month-abbr">{day.date.toFormat('MMM').toUpperCase()}</span>
                <span class="day-num">{day.date.day.toString().padStart(2, '0')}</span>
              </div>
              <div class="event-info">
                <span class="event-title">{day.title}</span>
                <span class="event-subtitle">{day.subtitle}</span>
              </div>
            </button>
          {/each}

          {#if month.topDays.length === 0}
            <div class="empty-events">
              <Icon icon={mdiCalendarBlank} size="18" />
              <span>No highlights</span>
            </div>
          {/if}
        </div>
      </div>
    {/each}
  </div>
</div>

<style>
  :global(:root) {
    --card-bg: #1e293b;
    --card-border: #334155;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --accent-color: #38bdf8;
    --date-box-bg: #0f172a;
  }

  .year-view-container {
    height: 100%;
    overflow-y: auto;
    background-color: #0f172a; /* Dark slate background */
    padding: 2rem;
    color: var(--text-primary);
  }

  /* Header Summary Styles */
  .summary-header {
    margin-bottom: 3rem;
  }

  .summary-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 2rem;
  }

  .summary-title {
    font-size: 3rem;
    font-weight: 800;
    color: white;
    margin: 0;
    line-height: 1.1;
  }

  .summary-subtitle {
    font-size: 1.25rem;
    color: var(--text-secondary);
    margin: 0.25rem 0 0 0;
    font-weight: 500;
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 1.5rem;
  }

  .nav-controls {
    display: flex;
    gap: 0.5rem;
  }

  .icon-btn {
    background: rgba(255, 255, 255, 0.05);
    border: none;
    color: var(--text-primary);
    padding: 0.5rem;
    border-radius: 50%;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .icon-btn:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: scale(1.1);
  }

  .stats-row {
    display: flex;
    gap: 1.5rem;
  }

  .stat-card {
    background: #162032; /* Slightly glossy/dark card */
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 1rem;
    padding: 1.5rem 2.5rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-width: 160px;
    box-shadow:
      0 4px 6px -1px rgba(0, 0, 0, 0.1),
      0 2px 4px -1px rgba(0, 0, 0, 0.06);
  }

  .stat-value {
    font-size: 2rem;
    font-weight: 800;
    color: white;
    line-height: 1;
    margin-bottom: 0.25rem;
  }

  .stat-label {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    color: var(--text-secondary);
    text-transform: uppercase;
  }

  /* Grid Layout */
  .cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 1.5rem;
    padding-bottom: 4rem;
  }

  /* Card Component */
  .month-card {
    background: #162032; /* Slightly lighter than bg */
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 1rem;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    height: 480px; /* Fixed height for consistency */
    transition:
      transform 0.2s,
      box-shadow 0.2s;
  }

  .month-card:hover {
    transform: translateY(-4px);
    box-shadow:
      0 20px 25px -5px rgba(0, 0, 0, 0.3),
      0 10px 10px -5px rgba(0, 0, 0, 0.2);
    border-color: rgba(255, 255, 255, 0.1);
  }

  /* Card Header / Cover */
  .card-header {
    width: 100%;
    height: 300px; /* 60% of card roughly */
    position: relative;
    padding: 0;
    border: none;
    cursor: pointer;
    background: #000;
    overflow: hidden;
  }

  .collage {
    width: 100%;
    height: 100%;
    display: flex;
  }

  .collage.multi {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 2px;
  }

  .collage-main {
    height: 100%;
    position: relative;
  }

  .collage-side {
    display: grid;
    grid-template-rows: 1fr 1fr;
    gap: 2px;
    height: 100%;
  }

  .month-card img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 0.5s ease;
  }

  .card-header:hover img {
    transform: scale(1.05);
  }

  .cover-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, rgba(0, 0, 0, 0.8) 0%, rgba(0, 0, 0, 0) 50%);
    pointer-events: none;
  }

  .empty-cover {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #1e293b;
    color: #475569;
  }

  .header-content {
    position: absolute;
    bottom: 0;
    left: 0;
    padding: 1.25rem;
    width: 100%;
    text-align: left;
    z-index: 2;
  }

  .month-name {
    font-size: 1.75rem;
    font-weight: 700;
    color: white;
    margin: 0;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
    text-transform: capitalize;
  }

  .count-badge {
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
    color: white;
    padding: 0.35rem 0.75rem;
    border-radius: 2rem;
    font-size: 0.75rem;
    font-weight: 600;
    z-index: 2;
    border: 1px solid rgba(255, 255, 255, 0.1);
  }

  /* Events List */
  .events-list {
    flex: 1;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    background: #162032;
    overflow-y: auto;
  }

  .event-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: transparent;
    border: none;
    padding: 0.5rem;
    border-radius: 0.5rem;
    cursor: pointer;
    text-align: left;
    transition: background 0.2s;
    width: 100%;
  }

  .event-item:hover {
    background: rgba(255, 255, 255, 0.05);
  }

  .date-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 0.5rem;
    width: 42px;
    height: 42px;
    flex-shrink: 0;
  }

  .month-abbr {
    font-size: 0.55rem;
    font-weight: 700;
    color: var(--accent-color);
    line-height: 1;
    margin-bottom: 2px;
  }

  .day-num {
    font-size: 0.9rem;
    font-weight: 700;
    color: white;
    line-height: 1;
  }

  .event-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
    overflow: hidden;
  }

  .event-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .event-subtitle {
    font-size: 0.7rem;
    color: var(--text-secondary);
  }

  .empty-events {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--text-secondary);
    font-size: 0.8rem;
    padding: 0.5rem;
    opacity: 0.5;
  }

  /* Responsive */
  @media (max-width: 1024px) {
    .cards-grid {
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    }
  }

  @media (max-width: 640px) {
    .year-view-container {
      padding: 1rem;
    }

    .cards-grid {
      grid-template-columns: 1fr;
    }

    .summary-title {
      font-size: 2rem;
    }

    .stats-row {
      gap: 1rem;
    }

    .stat-card {
      padding: 1rem;
      flex: 1;
    }

    .header-actions {
      align-items: flex-end;
    }
  }
</style>
