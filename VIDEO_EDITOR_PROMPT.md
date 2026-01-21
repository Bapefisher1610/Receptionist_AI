# 🎬 PROMPT: Xây dựng Video Editor & Creator Platform

## 📋 MỤC TIÊU DỰ ÁN

Xây dựng một nền tảng web application hoàn chỉnh cho việc tạo và chỉnh sửa video với các tính năng chuyên nghiệp, giao diện hiện đại, và trải nghiệm người dùng mượt mà.

---

## 🎯 YÊU CẦU CHỨC NĂNG CHÍNH

### 1. **TRANG TẠO VIDEO (Create Video Page)**

#### A. Upload & Import
- **Multi-source Upload**:
  - Upload từ máy tính (drag & drop, file browser)
  - Import từ URL (YouTube, Vimeo, direct links)
  - Import từ cloud storage (Google Drive, Dropbox, OneDrive)
  - Webcam recording (record trực tiếp)
  - Screen recording (capture màn hình)
  
- **Supported Formats**:
  - Video: MP4, MOV, AVI, MKV, WebM, FLV
  - Audio: MP3, WAV, AAC, OGG, M4A
  - Image: JPG, PNG, GIF, SVG, WebP
  - Subtitle: SRT, VTT, ASS

- **Batch Upload**:
  - Upload nhiều files cùng lúc
  - Progress bar cho từng file
  - Queue management
  - Auto-organize vào timeline

#### B. Timeline Editor (Trục thời gian)
- **Multi-track Timeline**:
  - Video tracks (nhiều layers)
  - Audio tracks (background music, voiceover, sound effects)
  - Text/Subtitle tracks
  - Effect tracks
  - Transition tracks

- **Timeline Controls**:
  - Zoom in/out timeline (scale thời gian)
  - Snap to grid (căn chỉnh tự động)
  - Ruler với timestamps
  - Playhead với frame-accurate positioning
  - Markers & bookmarks
  - Loop region selection

- **Clip Management**:
  - Drag & drop clips
  - Trim/Split/Cut clips
  - Copy/Paste/Duplicate
  - Ripple delete (xóa và tự động lấp khoảng trống)
  - Group/Ungroup clips
  - Lock/Unlock tracks

#### C. Video Editing Tools

**Basic Editing:**
- Cut/Trim: Cắt video tại điểm bất kỳ
- Split: Chia video thành nhiều phần
- Merge: Ghép nhiều video lại
- Speed Control: Tăng/giảm tốc độ (0.25x - 4x)
- Reverse: Đảo ngược video
- Rotate: Xoay video (90°, 180°, 270°)
- Flip: Lật ngang/dọc
- Crop: Cắt khung hình
- Resize: Thay đổi kích thước

**Advanced Editing:**
- Keyframe Animation: Tạo animation cho properties
- Motion Tracking: Theo dõi đối tượng
- Chroma Key (Green Screen): Xóa phông nền
- Picture-in-Picture (PiP): Video trong video
- Split Screen: Chia màn hình nhiều video
- Freeze Frame: Đóng băng khung hình
- Time Remapping: Điều chỉnh tốc độ động

#### D. Effects & Filters

**Visual Effects:**
- Color Grading:
  - Brightness/Contrast
  - Saturation/Hue
  - Temperature/Tint
  - Shadows/Highlights
  - RGB Curves
  - Color Wheels
  - LUTs (Look-Up Tables)

- Filters Library:
  - Vintage/Retro
  - Black & White
  - Sepia
  - Vignette
  - Blur (Gaussian, Motion, Radial)
  - Sharpen
  - Noise/Grain
  - Glitch Effects
  - Cinematic Presets

- Visual Effects:
  - Lens Flare
  - Light Leaks
  - Particles
  - Bokeh
  - Distortion
  - Chromatic Aberration
  - Film Grain

**Audio Effects:**
- Volume Control & Normalization
- Fade In/Out
- Equalizer (EQ)
- Noise Reduction
- Echo/Reverb
- Pitch Shift
- Audio Ducking (tự động giảm nhạc nền khi có voice)
- Compressor/Limiter

#### E. Text & Titles

**Text Tools:**
- Text Layers với full customization
- Font Library (Google Fonts integration)
- Text Animations:
  - Fade In/Out
  - Slide In/Out (từ 4 hướng)
  - Typewriter Effect
  - Bounce/Zoom
  - Rotate/Spin
  - Custom keyframe animations

**Text Styling:**
- Font family, size, weight
- Color & Gradient
- Stroke/Outline
- Shadow & Glow
- Background box
- Letter spacing & Line height
- Text alignment
- Opacity & Blend modes

**Title Templates:**
- Lower Thirds
- End Credits
- Opening Titles
- Subtitles/Captions
- Call-to-Action overlays
- Social Media Templates

#### F. Transitions

**Transition Library:**
- Fade (In/Out, Cross Dissolve)
- Wipe (Left, Right, Up, Down, Diagonal)
- Slide (Push, Cover, Uncover)
- Zoom (In, Out)
- Rotate/Spin
- Blur Transition
- Glitch Transition
- Morph/Distort
- 3D Transitions (Cube, Flip, Page Turn)

**Transition Controls:**
- Duration adjustment
- Easing curves (Linear, Ease In/Out, Bounce)
- Direction control
- Custom parameters

#### G. Audio Management

**Audio Editor:**
- Waveform visualization
- Multi-track audio mixing
- Volume keyframes
- Audio trimming & splitting
- Fade in/out curves
- Audio sync tools

**Audio Library:**
- Royalty-free music library
- Sound effects collection
- Voiceover recording
- Text-to-Speech integration
- Audio from video extraction

**Audio Features:**
- Beat detection & sync
- Audio spectrum visualization
- Noise gate
- Auto-ducking
- Audio normalization

#### H. Media Library & Assets

**Asset Management:**
- Media browser với thumbnails
- Search & filter
- Tags & categories
- Favorites/Collections
- Recent files
- Cloud storage integration

**Stock Assets:**
- Stock video library
- Stock images (Unsplash, Pexels integration)
- Stock music & sound effects
- Icons & graphics
- Animated stickers
- Background templates

#### I. AI-Powered Features

**AI Tools:**
- Auto-captions/Subtitles generation
- Speech-to-text transcription
- Auto-scene detection
- Smart crop (reframe for different aspect ratios)
- Background removal (AI-powered)
- Object removal
- Color matching
- Audio enhancement
- Smart suggestions

**AI Editing:**
- Auto-edit based on music beat
- Highlight detection
- Face detection & tracking
- Voice isolation
- Noise removal

---

### 2. **TRANG CHỈNH SỬA VIDEO (Edit Video Page)**

#### A. Advanced Timeline Features

**Timeline Enhancements:**
- Multi-camera editing
- Nested sequences (sequence trong sequence)
- Adjustment layers
- Blend modes
- Track matte
- 3D timeline view

**Precision Editing:**
- Frame-by-frame navigation (← →)
- Timecode display & input
- Snap to markers
- Ripple/Roll/Slip/Slide edits
- J-K-L playback control
- In/Out points marking

#### B. Professional Color Grading

**Color Tools:**
- Scopes (Waveform, Vectorscope, Histogram, RGB Parade)
- Primary color correction
- Secondary color correction (HSL keying)
- Color wheels (Lift, Gamma, Gain)
- Curves (Master, RGB, Hue vs Sat, Hue vs Hue)
- LUT support (import/export)
- Color match tool
- Skin tone protection

**Grading Presets:**
- Cinematic looks
- Film emulation
- Vintage styles
- Modern/Clean
- Custom presets save/load

#### C. Advanced Effects & Compositing

**Compositing:**
- Layer blending modes (20+ modes)
- Masks & Mattes:
  - Rectangle/Ellipse masks
  - Bezier path masks
  - Feathering & expansion
  - Mask tracking
  - Rotoscoping tools

**Advanced Effects:**
- Stabilization (video shake removal)
- Lens correction
- Perspective correction
- Morphing
- Displacement maps
- Particle systems
- 3D camera tracking

#### D. Motion Graphics

**Animation Tools:**
- Keyframe editor với graph view
- Bezier curve interpolation
- Motion paths
- Expression editor (JavaScript-based)
- Presets & templates

**Graphics:**
- Shape layers (rectangles, circles, polygons)
- Vector graphics support
- Animated infographics
- Charts & graphs
- Progress bars
- Countdown timers

#### E. Multi-format Export

**Export Presets:**
- Social Media:
  - YouTube (1080p, 4K, HDR)
  - Instagram (Feed, Stories, Reels)
  - TikTok
  - Facebook
  - Twitter
  - LinkedIn

- Professional:
  - ProRes (422, 4444)
  - DNxHD/DNxHR
  - H.264/H.265
  - AV1
  - Uncompressed

- Web:
  - MP4 (optimized)
  - WebM
  - GIF
  - Animated WebP

**Export Settings:**
- Resolution (720p - 8K)
- Frame rate (24, 25, 30, 60, 120 fps)
- Bitrate control (CBR, VBR)
- Audio codec & bitrate
- Metadata embedding
- Batch export
- Queue management

#### F. Collaboration Features

**Team Collaboration:**
- Real-time collaboration
- Comments & annotations
- Version history
- Share & review links
- Approval workflow
- Team libraries
- Cloud sync

**Project Management:**
- Project templates
- Auto-save & backup
- Project archiving
- Export project file
- Import from other editors

---

## 🎨 YÊU CẦU GIAO DIỆN (UI/UX)

### Design System

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  Header: Logo | Project Name | Save | Export | Share   │
├──────────┬──────────────────────────────────┬───────────┤
│          │                                  │           │
│  Media   │      Preview Window              │  Effects  │
│  Library │      (Video Player)              │  Panel    │
│          │                                  │           │
│  - Video ├──────────────────────────────────┤  - Color  │
│  - Audio │      Timeline                    │  - Audio  │
│  - Text  │      (Multi-track)               │  - Text   │
│  - FX    │                                  │  - Trans  │
│          │                                  │           │
├──────────┴──────────────────────────────────┴───────────┤
│  Toolbar: Tools | Playback | Zoom | Settings            │
└─────────────────────────────────────────────────────────┘
```

**Color Scheme:**
- Dark theme (primary) - Professional video editing look
- Light theme (optional)
- Accent colors: Blue (#0066FF), Green (#00CC66)
- High contrast for readability

**Typography:**
- Headers: Inter, SF Pro, Segoe UI
- Body: System fonts
- Monospace: JetBrains Mono (for timecode)

**Components:**
- Modern, flat design
- Smooth animations (60fps)
- Responsive layout
- Keyboard shortcuts overlay
- Context menus
- Tooltips
- Progress indicators

### User Experience

**Onboarding:**
- Welcome tutorial
- Interactive guide
- Template gallery
- Quick start projects
- Video tutorials

**Performance:**
- Proxy workflow (low-res preview)
- Background rendering
- GPU acceleration
- Optimized playback
- Smart caching

**Accessibility:**
- Keyboard navigation
- Screen reader support
- High contrast mode
- Customizable shortcuts
- Undo/Redo (unlimited)

---

## 🛠️ TECH STACK ĐỀ XUẤT

### Frontend
```javascript
// Core
- React 18+ (với Hooks)
- TypeScript
- Vite (build tool)

// State Management
- Redux Toolkit / Zustand
- React Query (server state)

// UI Framework
- Tailwind CSS
- Shadcn/ui hoặc Material-UI
- Framer Motion (animations)

// Video Processing
- FFmpeg.wasm (browser-based video processing)
- Video.js / Plyr (video player)
- WaveSurfer.js (audio waveform)
- Fabric.js (canvas manipulation)

// Timeline
- React DnD (drag & drop)
- Custom timeline component
- Konva.js (canvas rendering)

// File Upload
- React Dropzone
- Uppy (advanced upload)

// Charts & Visualization
- D3.js / Recharts
```

### Backend
```javascript
// Server
- Node.js + Express / Fastify
- Python + FastAPI (for AI features)

// Database
- PostgreSQL (metadata)
- Redis (caching, sessions)
- MongoDB (logs, analytics)

// Storage
- AWS S3 / Google Cloud Storage
- CDN (CloudFlare, AWS CloudFront)

// Video Processing
- FFmpeg (server-side)
- MediaConvert (AWS)
- Transcoder API (Google Cloud)

// AI/ML
- TensorFlow.js
- OpenAI API (captions, suggestions)
- Whisper (speech-to-text)
```

### Infrastructure
```yaml
# Deployment
- Docker + Kubernetes
- AWS / Google Cloud / Azure
- CI/CD: GitHub Actions

# Monitoring
- Sentry (error tracking)
- LogRocket (session replay)
- Google Analytics

# Performance
- CDN for assets
- WebSocket for real-time
- Worker threads for processing
```

---

## 📦 CẤU TRÚC DỰ ÁN

```
video-editor-platform/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Editor/
│   │   │   │   ├── Timeline/
│   │   │   │   ├── Preview/
│   │   │   │   ├── MediaLibrary/
│   │   │   │   ├── EffectsPanel/
│   │   │   │   └── Toolbar/
│   │   │   ├── CreateVideo/
│   │   │   ├── Export/
│   │   │   └── Shared/
│   │   ├── hooks/
│   │   ├── store/
│   │   ├── utils/
│   │   ├── services/
│   │   └── types/
│   ├── public/
│   └── package.json
│
├── backend/
│   ├── src/
│   │   ├── api/
│   │   ├── services/
│   │   ├── models/
│   │   ├── middleware/
│   │   └── utils/
│   ├── workers/
│   └── package.json
│
├── ai-service/
│   ├── models/
│   ├── api/
│   └── requirements.txt
│
└── docker-compose.yml
```

---

## 🚀 ROADMAP PHÁT TRIỂN

### Phase 1: MVP (2-3 tháng)
- [ ] Basic video upload & preview
- [ ] Simple timeline editor
- [ ] Cut, trim, split tools
- [ ] Basic transitions & effects
- [ ] Text overlay
- [ ] Export to MP4

### Phase 2: Core Features (2-3 tháng)
- [ ] Multi-track timeline
- [ ] Audio editing
- [ ] Advanced effects library
- [ ] Color correction
- [ ] Template system
- [ ] Cloud storage integration

### Phase 3: Advanced Features (3-4 tháng)
- [ ] AI-powered tools
- [ ] Collaboration features
- [ ] Motion graphics
- [ ] Advanced compositing
- [ ] Professional export options
- [ ] Mobile app

### Phase 4: Enterprise (Ongoing)
- [ ] Team management
- [ ] API access
- [ ] White-label solution
- [ ] Advanced analytics
- [ ] Custom integrations

---

## 💡 TÍNH NĂNG ĐỘC ĐÁO

1. **AI Smart Edit**: Tự động tạo video từ raw footage
2. **Voice Commands**: Điều khiển bằng giọng nói
3. **Real-time Collaboration**: Nhiều người edit cùng lúc
4. **Template Marketplace**: Mua/bán templates
5. **Brand Kit**: Lưu colors, fonts, logos của brand
6. **Auto-subtitle**: 100+ ngôn ngữ
7. **Smart Resize**: Tự động crop cho mọi platform
8. **Version Control**: Git-like cho video projects

---

## 📊 METRICS & KPIs

**Performance:**
- Page load time < 2s
- Video preview latency < 100ms
- Export speed: 2x realtime minimum
- 99.9% uptime

**User Experience:**
- Time to first edit < 30s
- Learning curve < 5 minutes
- User satisfaction > 4.5/5
- Retention rate > 60%

---

## 🔒 BẢO MẬT & PRIVACY

- End-to-end encryption cho projects
- GDPR compliant
- SOC 2 certification
- Regular security audits
- Data backup & recovery
- User data deletion on request

---

## 📝 DOCUMENTATION YÊU CẦU

1. **User Guide**: Hướng dẫn sử dụng chi tiết
2. **API Documentation**: REST API docs
3. **Developer Guide**: Setup & contribution
4. **Video Tutorials**: Screen recordings
5. **FAQ**: Câu hỏi thường gặp
6. **Changelog**: Version history

---

## 🎯 TARGET USERS

1. **Content Creators**: YouTubers, TikTokers
2. **Marketing Teams**: Social media managers
3. **Educators**: Online course creators
4. **Businesses**: Corporate videos
5. **Freelancers**: Video editors
6. **Agencies**: Production companies

---

## 💰 MONETIZATION

1. **Freemium Model**:
   - Free: 720p export, watermark, 5 projects
   - Pro: $15/month - 4K, no watermark, unlimited
   - Business: $49/month - Team features, API access

2. **Additional Revenue**:
   - Template marketplace (commission)
   - Stock assets (subscription)
   - Enterprise licenses
   - White-label solutions

---

## ✅ CHECKLIST HOÀN THÀNH

### Must Have:
- [ ] Video upload & import
- [ ] Timeline editor
- [ ] Basic editing tools
- [ ] Effects & transitions
- [ ] Text & titles
- [ ] Audio editing
- [ ] Export functionality
- [ ] User authentication
- [ ] Project save/load

### Should Have:
- [ ] AI features
- [ ] Collaboration
- [ ] Templates
- [ ] Stock library
- [ ] Mobile responsive
- [ ] Keyboard shortcuts
- [ ] Undo/Redo

### Nice to Have:
- [ ] Mobile app
- [ ] Voice control
- [ ] AR/VR support
- [ ] Live streaming
- [ ] Plugin system

---

## 📞 SUPPORT & MAINTENANCE

- 24/7 customer support
- Community forum
- Discord server
- Regular updates (bi-weekly)
- Bug bounty program
- Feature request voting

---

**Lưu ý**: Đây là một dự án lớn và phức tạp. Nên bắt đầu với MVP và dần dần thêm features theo feedback của users.
