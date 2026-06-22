# RecruitAI Platform - Complete UI/UX Plan

## 🎯 Vision
Build a world-class B2B recruitment platform that competes with Gem, Lever, Greenhouse, and iCIMS. Every interaction should feel polished, intuitive, and professional.

---

## 📁 Page Structure & Components

### 1. **Dashboard** ✅ (Partially Done)
**Purpose:** At-a-glance overview of recruitment pipeline

| Section | Components | Interactions |
|---------|-----------|--------------|
| Stats Cards | Applicant, Interviewed, Hired | Hover lift, click to drill-down |
| Open Position Chart | Donut chart | Hover tooltips, filter by department |
| Overview Chart | Bar + Line combo | Date range picker, toggle metrics |
| Daily Task Table | Task list with status | Filter, sort, bulk actions |
| Schedule Panel | Calendar + interviews | Day selection, tab switch |

**Missing/To Add:**
- Quick actions floating button
- Notification toast for new applications
- Activity feed/recent actions widget
- Team performance mini-chart

---

### 2. **Jobs / Job Descriptions**
**Purpose:** Create, manage, and track job postings

| Sub-page | Components | Interactions |
|----------|-----------|--------------|
| Jobs List | Data table, search, filters | Sort, filter by status/dept |
| Job Card | Status badge, applicant count | Click to view, quick actions menu |
| Create Job | Multi-step form | Progress indicator, auto-save |
| Job Detail | Tabs (Overview, Applicants, Pipeline) | Tab switch, inline edit |
| Job Preview | Desktop/mobile preview toggle | Live preview updates |

**Components:**
- `JobListPage` - Main jobs listing
- `JobCard` - Individual job card
- `CreateJobForm` - Multi-step job creation wizard
- `JobDetailView` - Full job details with tabs
- `JobPreviewModal` - Preview before publishing

---

### 3. **Candidates / Applications**
**Purpose:** View and manage all candidates across jobs

| Sub-page | Components | Interactions |
|----------|-----------|--------------|
| Candidates Grid | Card grid or list view | Toggle view, bulk select |
| Candidate Card | Avatar, score, status, job | Hover preview, quick actions |
| Candidate Detail | Full profile with tabs | Tab switch, stage progression |
| Resume Viewer | PDF viewer with highlights | Zoom, annotate, download |
| Activity Timeline | Chronological actions | Expand/collapse, filter |

**Components:**
- `CandidatesListPage` - Main candidates view
- `CandidateCard` - Individual candidate card
- `CandidateDetailView` - Full profile
- `ResumeViewer` - PDF resume with AI highlights
- `ActivityTimeline` - Candidate journey timeline
- `StageProgression` - Pipeline stage movement

---

### 4. **Resume Upload & Analysis**
**Purpose:** Upload resumes and get AI-powered analysis

| Sub-page | Components | Interactions |
|----------|-----------|--------------|
| Upload Zone | Drag & drop area | Drag hover effect, progress |
| Processing Queue | Upload status list | Real-time updates, cancel |
| Analysis Results | Score breakdown, skills | Animated score reveal |
| Bulk Upload | CSV/ZIP upload | Validation, error handling |

**Components:**
- `ResumeUploadZone` - Drag & drop with animation
- `ProcessingQueue` - Real-time processing status
- `AnalysisResults` - AI score visualization
- `BulkUploadModal` - Batch upload interface
- `SkillsMatchChart` - Skills visualization

---

### 5. **AI Interview Questions**
**Purpose:** Generate and manage interview questions

| Sub-page | Components | Interactions |
|----------|-----------|--------------|
| Question Bank | Categorized questions | Drag to reorder, edit inline |
| Generate Questions | AI generation form | Loading animation, edit results |
| Question Set | Grouped by type/skill | Expand/collapse, export |
| Custom Questions | Add/edit/delete | Inline editing, validation |

**Components:**
- `QuestionBank` - Main question management
- `QuestionGenerator` - AI question creation
- `QuestionCard` - Individual question display
- `QuestionSetBuilder` - Group questions by criteria
- `ExportQuestionsModal` - Export options

---

### 6. **Interview Evaluation**
**Purpose:** Score and evaluate candidates post-interview

| Sub-page | Components | Interactions |
|----------|-----------|--------------|
| Evaluation Form | Rating sliders, notes | Star ratings, auto-save |
| Score Comparison | Side-by-side scores | Toggle candidates |
| Feedback Collection | Multi-reviewer input | Submit, edit, delete |
| Evaluation Summary | Aggregated scores | Export, share |

**Components:**
- `EvaluationForm` - Interview scorecard
- `ScoreComparison` - Compare multiple candidates
- `FeedbackCollector` - Gather team feedback
- `EvaluationSummary` - Aggregated results
- `RatingStars` - Interactive star rating

---

### 7. **Reports & Analytics**
**Purpose:** Insights into recruitment performance

| Sub-page | Components | Interactions |
|----------|-----------|--------------|
| Overview Dashboard | KPI cards, charts | Date range, drill-down |
| Pipeline Analytics | Funnel visualization | Filter by stage/time |
| Time-to-Hire | Timeline charts | Compare periods |
| Source Analytics | Channel performance | Filter by source |
| Team Performance | Recruiter metrics | Sort, compare |
| Export Center | Report generation | Schedule, download |

**Components:**
- `ReportsDashboard` - Main analytics view
- `PipelineFunnel` - Hiring funnel visualization
- `TimeToHireChart` - Duration analytics
- `SourcePerformance` - Channel metrics
- `TeamMetrics` - Recruiter performance
- `ExportPanel` - Report export options

---

### 8. **Candidate Ranking**
**Purpose:** AI-powered candidate ranking and comparison

| Sub-page | Components | Interactions |
|----------|-----------|--------------|
| Ranking List | Sorted candidates | Reorder, filter |
| Comparison View | Side-by-side profiles | Toggle attributes |
| Score Breakdown | Category scores | Expand details |
| Shortlist Builder | Drag to shortlist | Drag & drop, export |

**Components:**
- `RankingList` - Ranked candidates
- `ComparisonView` - Side-by-side comparison
- `ScoreBreakdown` - Detailed scoring
- `ShortlistBuilder` - Build shortlists
- `ExportShortlist` - Export to PDF/CSV

---

### 9. **Settings**
**Purpose:** Platform configuration and preferences

| Sub-page | Components | Interactions |
|----------|-----------|--------------|
| Profile Settings | User info, avatar | Upload, save |
| Company Settings | Org details, branding | Multi-tab form |
| Team Management | Member list, roles | Invite, remove, edit |
| Integrations | Connected apps | Connect, disconnect |
| Notifications | Alert preferences | Toggle switches |
| Billing | Plan, invoices | Upgrade, download |
| API & Webhooks | Keys, endpoints | Create, revoke |

**Components:**
- `SettingsLayout` - Settings navigation
- `ProfileSettings` - User profile form
- `CompanySettings` - Organization settings
- `TeamManagement` - Team member management
- `IntegrationsList` - Connected integrations
- `NotificationPreferences` - Alert settings
- `BillingPage` - Subscription management
- `APIKeysManager` - API key management

---

### 10. **Public Interview Page**
**Purpose:** Candidate-facing interview interface

| Sub-page | Components | Interactions |
|----------|-----------|--------------|
| Welcome Screen | Branding, instructions | Start button |
| Question Display | Question + timer | Next, skip, timeout |
| Response Input | Text/voice/video | Record, submit |
| Completion Screen | Thank you, next steps | Download confirmation |

**Components:**
- `InterviewWelcome` - Landing page
- `QuestionDisplay` - Interview question
- `ResponseInput` - Answer submission
- `InterviewComplete` - Completion screen

---

## 🧩 Reusable UI Components

### Layout Components
- `Sidebar` ✅ - Collapsible sidebar
- `Header` ✅ - Top navigation bar
- `PageHeader` ✅ - Page title + actions
- `Breadcrumbs` - Navigation breadcrumbs
- `Footer` - Page footer

### Data Display
- `DataTable` - Sortable, filterable table
- `Card` - Content card wrapper
- `StatCard` ✅ - Statistics display
- `ListItem` - List item with actions
- `Timeline` - Activity timeline
- `EmptyState` - No data placeholder
- `LoadingSkeleton` ✅ - Loading placeholder

### Forms
- `Input` - Text input
- `TextArea` - Multi-line input
- `Select` - Dropdown select
- `MultiSelect` - Multiple selection
- `Checkbox` - Checkbox input
- `Radio` - Radio button
- `Toggle` - On/off switch
- `DatePicker` - Date selection
- `TimePicker` - Time selection
- `FileUpload` - File upload zone
- `RichTextEditor` - Formatted text input

### Feedback
- `Toast` - Notification messages
- `Alert` - Alert banners
- `Modal` - Dialog windows
- `ConfirmDialog` - Confirmation prompts
- `Tooltip` - Hover information
- `Popover` - Click information
- `Progress` - Progress indicator
- `Spinner` - Loading spinner

### Navigation
- `Tabs` - Tab navigation
- `Pagination` - Page navigation
- `Stepper` - Step progress
- `Breadcrumbs` - Path breadcrumbs
- `DropdownMenu` - Action menus
- `CommandPalette` - Quick actions (⌘K)

### Data Visualization
- `BarChart` ✅ - Bar charts
- `LineChart` ✅ - Line charts
- `PieChart` ✅ - Pie/donut charts
- `FunnelChart` - Conversion funnel
- `HeatMap` - Data heatmap
- `RadarChart` - Skills visualization
- `GaugeChart` - Score display

---

## ✨ Interactions & Animations

### Page Transitions
```
Fade in/out (200ms)
Slide in from left (300ms)
Scale up from 95% (200ms)
```

### Component Animations
```
Card hover: translateY(-2px), shadow increase
Button click: scale(0.98)
Modal open: fade + scale from 95%
Toast slide: slide in from right, auto-dismiss
Sidebar collapse: width transition (300ms)
Dropdown: fade + translateY(-8px)
```

### Micro-interactions
```
Toggle switch: 150ms ease
Star rating: bounce on select
Status badge: pulse on new
Progress bar: animate width
Score reveal: count up animation
```

### Loading States
```
Skeleton screens (pulse animation)
Spinner for actions
Progress bars for uploads
Optimistic updates for toggles
```

---

## 🎨 Design System

### Colors
```
Primary: Indigo (50-900)
Success: Emerald (50-900)
Warning: Amber (50-900)
Error: Rose (50-900)
Info: Sky (50-900)
Neutral: Gray (50-900)
```

### Typography
```
Headings: Inter Bold (700)
Subheadings: Inter Semibold (600)
Body: Inter Regular (400)
Captions: Inter Medium (500)
```

### Spacing
```
xs: 4px
sm: 8px
md: 16px
lg: 24px
xl: 32px
2xl: 48px
```

### Border Radius
```
sm: 6px
md: 8px
lg: 12px
xl: 16px
2xl: 24px
full: 9999px
```

### Shadows
```
sm: 0 1px 2px rgba(0,0,0,0.05)
md: 0 4px 6px rgba(0,0,0,0.07)
lg: 0 10px 15px rgba(0,0,0,0.1)
xl: 0 20px 25px rgba(0,0,0,0.15)
```

---

## 🔧 Technical Implementation

### State Management
- React Context for global state (theme, user)
- URL state for filters/sorting
- Local state for forms/modals

### Data Fetching
- React Query for API calls
- Optimistic updates
- Cache invalidation
- Background refetch

### Forms
- React Hook Form + Zod validation
- Field-level validation
- Auto-save with debounce
- Form state persistence

### Routing
- React Router v6
- Nested routes
- Route guards (auth)
- Lazy loading

### Performance
- Code splitting by route
- Virtual scrolling for lists
- Image lazy loading
- Memoization for expensive calculations

---

## 📋 Build Order (Priority)

### Phase 1: Core Infrastructure
1. ✅ Theme system (light/dark)
2. ✅ Layout with collapsible sidebar
3. Reusable UI component library
4. Form components with validation
5. Toast notification system
6. Modal/dialog system

### Phase 2: Primary Features
7. Dashboard (enhance existing)
8. Jobs management (CRUD)
9. Candidates list & detail
10. Resume upload & analysis

### Phase 3: AI Features
11. Interview question generator
12. Candidate scoring/ranking
13. Resume parsing visualization
14. Smart matching display

### Phase 4: Collaboration
15. Interview evaluation
16. Team feedback system
17. Activity feed/comments
18. Email templates

### Phase 5: Analytics
19. Reports dashboard
20. Pipeline analytics
21. Export functionality
22. Scheduled reports

### Phase 6: Settings & Admin
23. Profile settings
24. Team management
25. Integrations
26. Billing/subscription

### Phase 7: Polish
27. Animations & transitions
28. Keyboard shortcuts
29. Accessibility (a11y)
30. Responsive optimization

---

## 🎯 Key Interactions to Implement

### Command Palette (⌘K)
- Quick search across all entities
- Navigate to any page
- Create new job/candidate
- Recent actions

### Bulk Actions
- Select multiple candidates
- Bulk status change
- Export selected
- Send bulk emails

### Drag & Drop
- Reorder pipeline stages
- Drag candidate to stage
- Reorder questions
- Organize dashboard widgets

### Real-time Updates
- New application notifications
- Interview status changes
- Team activity feed
- Processing status

### Keyboard Shortcuts
- `⌘K` - Command palette
- `⌘N` - New job
- `⌘/` - Search
- `Esc` - Close modal
- `←/→` - Navigate tabs

---

This plan covers every corner of a professional B2B recruitment platform. Ready to start building?
