import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const body = await request.json(); // Get username and password from the request body
    const { username, password } = body;

    // Create a FormData object to send form data
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)

    // Send the login credentials to the external API
    const externalApiResponse = await fetch('https://auto-nabavka.onrender.com/login/access-token', {
      method: 'POST',
      body: formData,
    });

    if (!externalApiResponse.ok) {
      return NextResponse.json({ error: 'Invalid credentials' }, { status: 401 });
    }

    const token = await externalApiResponse.json();

    // Set the JWT token in an HTTP-only cookie
    const response = NextResponse.json({ message: 'Login successful' });
    response.cookies.set('token', token.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      maxAge: 604800,
      path: '/',
    });

    return response;
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'An error occurred' }, { status: 500 });
  }
}
