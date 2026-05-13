import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

// These routes require login
const isProtectedRoute = createRouteMatcher([
  '/search(.*)',
  '/podcasts(.*)',
  '/episodes(.*)',
])

export default clerkMiddleware(async (auth, request) => {
  if (isProtectedRoute(request)) {
    await auth.protect()
  }
})

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jss?|img|font|ttf|woff2?|ico|csv|webmanifest)).*)',
    '/(api|trpc)(.*)',
  ],
}
