import { usePathname } from 'next/navigation';
import { NextResponse } from 'next/server';

export function middleware(request) {
  const token = request.cookies.get('token'); // Get the token from cookies
  const pathname = usePathname()

  if (!token) {
    // Redirect to login if token is missing
    return NextResponse.redirect(new URL('/login', request.url));
  }

  if (pathname === '/') {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // Allow the request to proceed if token is present
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard', '/test']
}
