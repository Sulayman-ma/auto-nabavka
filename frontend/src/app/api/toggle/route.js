import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const body = await request.json(); // Get username and password from the request body
    const { userId, token } = body;

    // Send the login credentials to the external API
    const response = await fetch(`https://auto-nabavka.onrender.com/api/users/toggle/${userId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      return NextResponse.json({ error: 'Failed to toggle user status' }, { status: 500 });
    }

    const data = await response.json();
    return new Response(JSON.stringify(data), { status: 200 });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'An error occurred' }, { status: 500 });
  }
}
