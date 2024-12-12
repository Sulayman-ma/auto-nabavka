import { NextResponse } from 'next/server';

export async function middleware(request) {
  const token = request.cookies.get('token'); // Get the token from cookies

  if (!token) {
    // Redirect to login if token is missing
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Verify token against test-token
  const response = await fetch("https://auto-nabavka.onrender.com/api/login/test-token", {
    method: "POST",
    headers: {
      'Authorization': `Bearer ${token.value}`
    }
  })
  if (!response.ok) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  if (request.nextUrl.pathname === '/') {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // Allow the request to proceed if token is present
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard', '/test', '/']
}
