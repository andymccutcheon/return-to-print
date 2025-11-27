# Receipt Me Frontend

A Next.js 14 web application for the Receipt Me thermal printer art installation. Users can submit messages that are queued and printed on a thermal receipt printer.

## Features

- **Message Submission**: Submit messages up to 280 characters
- **Real-time Validation**: Character counter with visual feedback
- **Recent Messages**: View the last 10 messages with print status
- **Responsive Design**: Mobile-first, works on all devices
- **Thermal Printer Aesthetic**: Clean, receipt-inspired design
- **Accessibility**: WCAG 2.1 AA compliant

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **Hosting**: AWS Amplify
- **API**: REST API backed by AWS Lambda

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API must be deployed

### Installation

1. Clone the repository and navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file (copy from `.env.example`):
```bash
cp .env.example .env.local
```

4. Update the API URL in `.env.local`:
```bash
NEXT_PUBLIC_API_BASE_URL=https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod
```

### Development

Run the development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Building for Production

```bash
npm run build
npm run start
```

### Type Checking

```bash
npm run type-check
```

### Linting

```bash
npm run lint
```

## Project Structure

```
frontend/
├── src/
│   ├── app/              # Next.js App Router pages
│   │   ├── layout.tsx    # Root layout with metadata
│   │   ├── page.tsx      # Main page
│   │   └── globals.css   # Global styles
│   ├── components/       # React components
│   │   ├── MessageForm.tsx    # Message submission form
│   │   └── MessageList.tsx    # Recent messages display
│   ├── lib/              # Utility functions
│   │   └── api.ts        # API client functions
│   └── types/            # TypeScript type definitions
│       └── message.ts    # Message-related types
├── public/               # Static assets
├── amplify.yml           # AWS Amplify build configuration
├── .env.local            # Environment variables (not in git)
├── .env.example          # Environment template
├── package.json
├── tsconfig.json
└── README.md
```

## Environment Variables

### Required

- `NEXT_PUBLIC_API_BASE_URL`: Backend API base URL
  - Example: `https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod`

## API Integration

The frontend communicates with two backend endpoints:

### POST /message
Creates a new message to be printed.

**Request:**
```json
{
  "content": "Message text (1-280 characters)"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "content": "Message text",
  "created_at": "2025-11-24T10:30:00Z",
  "printed": "false",
  "printed_at": null
}
```

### GET /messages/recent
Retrieves the 10 most recent messages.

**Response (200):**
```json
{
  "messages": [
    {
      "id": "uuid",
      "content": "...",
      "created_at": "2025-11-24T10:30:00Z",
      "printed": "true",
      "printed_at": "2025-11-24T10:31:00Z"
    }
  ]
}
```

### Important Notes

- The `printed` field is a **string** (`"true"` or `"false"`), not a boolean
- This is due to DynamoDB GSI constraints on the backend
- Always compare as: `message.printed === 'true'`

## Deployment

### AWS Amplify Setup

1. **Connect GitHub Repository**
   - Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify/)
   - Click "New app" → "Host web app"
   - Connect your GitHub repository
   - Branch: `main`
   - Root directory: `frontend/`

2. **Configure Build Settings**
   - Amplify will auto-detect Next.js
   - Use the `amplify.yml` configuration included in this repo

3. **Set Environment Variables**
   - Add `NEXT_PUBLIC_API_BASE_URL` in Amplify Console
   - Go to: App settings → Environment variables
   - Key: `NEXT_PUBLIC_API_BASE_URL`
   - Value: `https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod`

4. **Deploy**
   - Push to `main` branch
   - Amplify will automatically build and deploy

### Custom Domain

The app will be available at:
- **Amplify URL**: `https://main.d[app-id].amplifyapp.com`
- **Custom Domain** (when DNS propagates): `https://www.returntoprint.xyz`

## Component Documentation

### MessageForm

Handles message submission with validation.

**Props:**
- `onSuccess?: () => void` - Called after successful message creation

**Features:**
- Character counter (280 max)
- Real-time validation
- Loading states
- Success/error feedback
- Visual warning at 260+ characters

### MessageList

Displays recent messages with loading and empty states.

**Props:**
- `refreshTrigger?: number` - Change to trigger refresh

**Features:**
- Loading skeleton
- Empty state
- Print status indicator
- Timestamp formatting
- Manual refresh button

## Accessibility

- Semantic HTML5 elements
- ARIA labels and roles
- Keyboard navigation support
- Screen reader friendly
- Focus visible indicators
- Reduced motion support

## Performance

- Server-side rendering with Next.js
- Code splitting by route
- Image optimization (Next.js Image component)
- Tailwind CSS purging
- Incremental Static Regeneration ready

## Browser Support

- Chrome (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)
- Edge (last 2 versions)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Testing

### Manual Testing Checklist

- [ ] Submit a valid message
- [ ] Verify character counter accuracy
- [ ] Test empty message validation
- [ ] Test 280+ character validation
- [ ] Verify message list refreshes after submission
- [ ] Check print status displays correctly
- [ ] Test responsive layout on mobile
- [ ] Verify error messages display
- [ ] Test keyboard navigation
- [ ] Check screen reader compatibility

## Troubleshooting

### API Connection Issues

If the API is unreachable:
1. Check `NEXT_PUBLIC_API_BASE_URL` is set correctly
2. Verify the backend API is deployed and running
3. Check browser console for CORS errors
4. Test API directly: `curl https://[API-URL]/messages/recent`

### Build Errors

If the build fails:
1. Run `npm install` to ensure dependencies are installed
2. Run `npm run type-check` to find TypeScript errors
3. Run `npm run lint` to find ESLint errors
4. Check that all environment variables are set

## Contributing

This is part of the Receipt Me project. See the main repository for contribution guidelines.

## License

Part of the Receipt Me thermal printer art installation project.

---

**Status**: ✅ Production Ready  
**Last Updated**: November 24, 2025  
**Version**: 1.0.0
