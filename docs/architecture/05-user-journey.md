# User Journey Diagram

## Purpose
End-to-end user workflows showing how users interact with the system from login through various voting and navigation scenarios.

## Main User Flows

```mermaid
flowchart TD
    Start([User arrives at app]) --> Login{Logged in?}
    Login -->|No| LoginPage[Login Page]
    Login -->|Yes| Index[Index Page<br/>All Records]
    
    LoginPage --> EnterUsername[Enter Username]
    EnterUsername --> ValidateUsername{Valid username?}
    ValidateUsername -->|No| ShowError[Show Error Message]
    ShowError --> EnterUsername
    ValidateUsername -->|Yes| CheckUser{User exists?}
    
    CheckUser -->|No| CreateUser[Create User Account]
    CheckUser -->|Yes| GetUser[Get Existing User]
    
    CreateUser --> CheckAdmin{Username = Admin?}
    GetUser --> CheckAdmin
    CheckAdmin -->|Yes| SetAdmin[Set is_admin = True]
    CheckAdmin -->|No| SetRegular[Set is_admin = False]
    
    SetAdmin --> CreateSession[Create Session<br/>username, user_id, is_admin]
    SetRegular --> CreateSession
    CreateSession --> Index
    
    Index --> BrowseRecords[Browse Record List]
    BrowseRecords --> SelectRecord[Click Record]
    SelectRecord --> RecordDetail[Record Detail Page<br/>View Notes]
    
    RecordDetail --> ViewNote[View Note Text]
    ViewNote --> Decision{Make Decision}
    
    Decision -->|Need Translation| Translate[Click Translate Button<br/>Open Google Translate]
    Translate --> ViewNote
    
    Decision -->|See Other Votes| ToggleVotes[Click Show Other Votes]
    ToggleVotes --> ViewVotes[View Vote Distribution<br/>Consensus, Voters]
    ViewVotes --> Decision
    
    Decision -->|Vote| CheckBulk{Identical Notes<br/>Checkbox?}
    CheckBulk -->|Yes| BulkVote[Check Vote All Identical]
    CheckBulk -->|No| SingleVote[Click Classification Button]
    BulkVote --> SingleVote
    
    SingleVote --> SubmitVote[AJAX POST /vote<br/>or /vote-identical]
    SubmitVote --> ProcessVote[Backend Processes Vote]
    ProcessVote --> UpdateUI[Update UI<br/>Distribution, Consensus,<br/>Button Highlighting]
    UpdateUI --> ShowNotification[Show Success Notification]
    ShowNotification --> Navigate{Next Action?}
    
    Navigate -->|Next Record| NextRecord[Click Next Record]
    Navigate -->|Previous Record| PrevRecord[Click Previous Record]
    Navigate -->|Quick Jump| QuickNav[Use Quick Navigation]
    Navigate -->|Filter View| FilterView[Go to Filter View]
    Navigate -->|Continue| ViewNote
    
    NextRecord --> RecordDetail
    PrevRecord --> RecordDetail
    
    QuickNav --> QuickNavOptions{Quick Nav Option}
    QuickNavOptions -->|Unclassified| NextUnclassified[Next Unclassified]
    QuickNavOptions -->|Unknown| NextUnknown[Next Unknown]
    QuickNavOptions -->|Pending Review| NextPending[Next Pending Review]
    
    NextUnclassified --> RecordDetail
    NextUnknown --> RecordDetail
    NextPending --> RecordDetail
    
    FilterView --> FilterOptions{Filter Type}
    FilterOptions -->|Unknown| UnknownFilter[Unknown Records<br/>Consensus = ?]
    FilterOptions -->|Pending| PendingFilter[Pending Review<br/>User hasn't voted]
    FilterOptions -->|Contentious| ContentiousFilter[Contentious Records<br/>Low consensus]
    
    UnknownFilter --> SelectRecord
    PendingFilter --> SelectRecord
    ContentiousFilter --> SelectRecord
    
    RecordDetail --> KeyboardNav{Keyboard Input?}
    KeyboardNav -->|Left Arrow| PrevRecord
    KeyboardNav -->|Right Arrow| NextRecord
    
    Index --> AdminCheck{Is Admin?}
    AdminCheck -->|Yes| AdminNav[Admin Navigation Visible]
    AdminCheck -->|No| RegularNav[Regular Navigation Only]
    
    AdminNav --> AdminClick[Click Admin Link]
    AdminClick --> AdminDashboard[Admin Dashboard<br/>Statistics]
    
    AdminDashboard --> AdminOptions{Admin Action}
    AdminOptions -->|Upload XML| UploadXML[Upload XML File]
    AdminOptions -->|Export XML| ExportXML[Export Classifications]
    AdminOptions -->|Settings| AdminSettings[Configure Settings]
    AdminOptions -->|View Stats| ViewStats[View Statistics]
    
    UploadXML --> SelectFile[Select XML File]
    SelectFile --> CreateVotes{Create Initial Votes?}
    CreateVotes -->|Yes| ParseWithVotes[Parse XML<br/>Create Records/Notes/Votes]
    CreateVotes -->|No| ParseOnly[Parse XML<br/>Create Records/Notes Only]
    
    ParseWithVotes --> ImportComplete[Import Complete<br/>Show Results]
    ParseOnly --> ImportComplete
    ImportComplete --> AdminDashboard
    
    ExportXML --> SetThreshold[Set Confidence Threshold]
    SetThreshold --> IncludeStats{Include Stats?}
    IncludeStats -->|Yes| ExportWithStats[Export with<br/>vote_count, consensus_probability]
    IncludeStats -->|No| ExportBasic[Export Basic XML]
    
    ExportWithStats --> DownloadXML[Download XML File]
    ExportBasic --> DownloadXML
    DownloadXML --> AdminDashboard
    
    AdminSettings --> SetContentious[Set Contentious Threshold<br/>Default: 70%]
    SetContentious --> SetMinVotes[Set Min Votes for Contentious<br/>Default: 3]
    SetMinVotes --> SaveSettings[Save Settings]
    SaveSettings --> AdminDashboard
    
    ViewStats --> ViewContributors[View Top Contributors]
    ViewContributors --> ViewDistribution[View Classification Distribution]
    ViewDistribution --> ViewActivity[View Recent Activity]
    ViewActivity --> AdminDashboard
    
    Index --> Logout[Click Logout]
    Logout --> ClearSession[Clear Session]
    ClearSession --> LoginPage
```

## Detailed Voting Flow

```mermaid
flowchart LR
    A[User Views Note] --> B{User Decision}
    B -->|Need Info| C[Show Other Votes]
    B -->|Need Translation| D[Open Google Translate]
    B -->|Ready to Vote| E[Select Classification]
    
    C --> F[View Distribution<br/>Consensus: W 75%<br/>Voters: user1, user2]
    F --> B
    
    D --> G[Google Translate Page]
    G --> B
    
    E --> H{Identical Notes<br/>Checkbox?}
    H -->|Checked| I[Bulk Vote Mode]
    H -->|Unchecked| J[Single Vote Mode]
    
    I --> K[Submit to /vote-identical<br/>note_text + classification]
    J --> L[Submit to /vote<br/>bib_id + note_index + classification]
    
    K --> M[Backend Processes]
    L --> M
    
    M --> N[Create/Update Vote]
    N --> O[Calculate Distribution]
    O --> P[Return JSON Response]
    
    P --> Q[Update UI]
    Q --> R[Highlight Button]
    Q --> S[Show Distribution]
    Q --> T[Show Notification]
    
    R --> U[Continue Voting]
    S --> U
    T --> U
    
    U --> V{Next Action}
    V -->|Next Note| W[Scroll to Next Note]
    V -->|Next Record| X[Navigate to Next Record]
    V -->|Filter View| Y[Go to Filter]
    
    W --> A
    X --> A
    Y --> A
```

## Navigation Patterns

```mermaid
flowchart TD
    Start([User at Record Detail]) --> NavOptions{Navigation Method}
    
    NavOptions -->|Mouse Click| MouseNav[Mouse Navigation]
    NavOptions -->|Keyboard| KeyboardNav[Keyboard Navigation]
    NavOptions -->|Quick Jump| QuickNav[Quick Navigation]
    NavOptions -->|Filter| FilterNav[Filter Navigation]
    
    MouseNav --> MouseOptions{Mouse Action}
    MouseOptions -->|Previous Button| PrevMouse[← Previous Record]
    MouseOptions -->|Next Button| NextMouse[Next Record →]
    MouseOptions -->|Back to Records| BackMouse[← Back to Records]
    
    KeyboardNav --> KeyOptions{Key Pressed}
    KeyOptions -->|Left Arrow| PrevKey[← Previous Record]
    KeyOptions -->|Right Arrow| NextKey[Next Record →]
    
    QuickNav --> QuickOptions{Quick Nav Type}
    QuickOptions -->|Unclassified| UnclassifiedNav[Next Unclassified<br/>No votes yet]
    QuickOptions -->|Unknown| UnknownNav[Next Unknown<br/>Consensus = ?]
    QuickOptions -->|Pending| PendingNav[Next Pending Review<br/>User hasn't voted]
    
    FilterNav --> FilterOptions{Filter Type}
    FilterOptions -->|Unknown| UnknownFilter[Unknown Page<br/>All records with ? consensus]
    FilterOptions -->|Pending| PendingFilter[Pending Review Page<br/>All unvoted notes]
    FilterOptions -->|Contentious| ContentiousFilter[Contentious Page<br/>Low consensus notes]
    
    PrevMouse --> RecordDetail[Record Detail Page]
    NextMouse --> RecordDetail
    BackMouse --> Index[Index Page]
    PrevKey --> RecordDetail
    NextKey --> RecordDetail
    UnclassifiedNav --> RecordDetail
    UnknownNav --> RecordDetail
    PendingNav --> RecordDetail
    UnknownFilter --> RecordDetail
    PendingFilter --> RecordDetail
    ContentiousFilter --> RecordDetail
    
    RecordDetail --> Start
    Index --> Start
```

## Admin Workflows

```mermaid
flowchart TD
    AdminLogin[Admin Logs In] --> AdminDashboard[Admin Dashboard]
    
    AdminDashboard --> AdminMenu{Admin Menu}
    
    AdminMenu -->|Dashboard| ViewDashboard[View Statistics<br/>- Total records/notes/votes<br/>- Top contributors<br/>- Classification distribution<br/>- Recent activity]
    
    AdminMenu -->|Upload XML| UploadFlow[Upload XML Flow]
    AdminMenu -->|Export XML| ExportFlow[Export XML Flow]
    AdminMenu -->|Settings| SettingsFlow[Settings Flow]
    
    UploadFlow --> SelectXML[Select XML File]
    SelectXML --> ChooseVotes{Create Initial Votes<br/>from type attributes?}
    ChooseVotes -->|Yes| ImportWithVotes[Import with Votes<br/>Creates Records, Notes, Votes]
    ChooseVotes -->|No| ImportWithoutVotes[Import without Votes<br/>Creates Records, Notes only]
    
    ImportWithVotes --> ImportResults[Show Import Results<br/>- Records created<br/>- Notes created<br/>- Votes created<br/>- Errors if any]
    ImportWithoutVotes --> ImportResults
    ImportResults --> AdminDashboard
    
    ExportFlow --> SetConfidence[Set Confidence Threshold<br/>Default: 60%]
    SetConfidence --> ChooseStats{Include Statistics?}
    ChooseStats -->|Yes| ExportWithStats[Export with Stats<br/>vote_count, consensus_probability]
    ChooseStats -->|No| ExportBasic[Export Basic XML]
    
    ExportWithStats --> GenerateXML[Generate XML File<br/>Filter by confidence<br/>Include consensus]
    ExportBasic --> GenerateXML
    GenerateXML --> DownloadFile[Download XML File]
    DownloadFile --> AdminDashboard
    
    SettingsFlow --> SetThreshold[Set Contentious Threshold<br/>0-1, Default: 0.70]
    SetThreshold --> SetMinVotes[Set Min Votes for Contentious<br/>Default: 3]
    SetMinVotes --> SaveSettings[Save Settings]
    SaveSettings --> ConfirmSettings[Settings Updated<br/>Flash Message]
    ConfirmSettings --> AdminDashboard
    
    ViewDashboard --> AdminDashboard
```

## Error Scenarios

```mermaid
flowchart TD
    UserAction[User Action] --> ErrorCheck{Error Occurs?}
    
    ErrorCheck -->|No| Success[Success Path]
    ErrorCheck -->|Yes| ErrorType{Error Type}
    
    ErrorType -->|Not Logged In| AuthError[Redirect to Login<br/>Flash: Please log in]
    ErrorType -->|Invalid Classification| ValidationError[400 Bad Request<br/>Show: Invalid classification]
    ErrorType -->|Record Not Found| NotFoundError[404 Not Found<br/>Show: Record not found]
    ErrorType -->|Database Error| DBError[500 Server Error<br/>Show: Database error]
    ErrorType -->|Network Error| NetworkError[Show: Network error occurred]
    
    AuthError --> LoginPage[Login Page]
    ValidationError --> StayOnPage[Stay on Current Page<br/>Show Error Notification]
    NotFoundError --> StayOnPage
    DBError --> StayOnPage
    NetworkError --> StayOnPage
    
    LoginPage --> RetryAction[User Logs In<br/>Retries Action]
    StayOnPage --> RetryAction
    RetryAction --> UserAction
```

## User Journey Characteristics

### Regular User Journey
1. **Login** → Simple username entry, no password
2. **Browse** → View list of all records
3. **Classify** → Vote on notes, see consensus
4. **Navigate** → Use filters, quick navigation, keyboard shortcuts
5. **Review** → Check contentious notes, unknown classifications

### Admin User Journey
1. **Login** → Username "Admin" grants admin privileges
2. **Dashboard** → View statistics and activity
3. **Import** → Upload XML files to populate database
4. **Export** → Download classifications with confidence filtering
5. **Configure** → Adjust contentious thresholds and settings

### Key User Experience Features
- **Vote Privacy**: Other users' votes hidden by default
- **Bulk Voting**: Vote on all identical notes at once
- **Translation**: Quick access to Google Translate
- **Keyboard Navigation**: Arrow keys for quick movement
- **Quick Navigation**: Jump to next unclassified/unknown/pending
- **Filter Views**: Dedicated pages for specific note types
- **Progress Tracking**: Visual progress meter through records
- **Real-time Updates**: AJAX updates without page reload

## Decision Points

### When to Show Other Votes
- User clicks "Show Other Votes" button
- Votes are hidden by default to prevent bias
- Can toggle visibility on/off

### When to Use Bulk Voting
- Note has "X identical" badge
- User checks "Vote on all X identical notes"
- Applies vote to all notes with matching text

### When to Mark as Contentious
- Consensus probability < threshold (default 70%)
- Total votes >= min_votes (default 3)
- Visual badge displayed on note

### When to Export Notes
- Admin sets confidence threshold
- Only notes with consensus_probability >= threshold exported
- Optional statistics included in XML attributes
