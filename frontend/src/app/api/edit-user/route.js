import { cookies } from "next/headers";

export async function PATCH(req) {
  const { userId, updatedUserData } = await req.json();

  try {
    // Fetch token from cookies
    const token = (await cookies()).get('token')

    // Return unauthorized if token is missing
    if (!token) {
      return new Response(JSON.stringify({ message: 'No token found' }), { status: 401 });
    }

    // Make the request to the API
    const response = await fetch(`https://auto-nabavka.onrender.com/api/users/${userId}`, {
      method: 'PATCH',
      headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token.value}`
      },
      body: JSON.stringify(updatedUserData),
    });

    if (!response.ok) {
      return new Response(JSON.stringify({ message: 'Failed to update user' }), { status: 500 });
    }

    const data = await response.json();
    return new Response(JSON.stringify(data), { status: 200 });
  } catch (error) {
    return new Response(JSON.stringify({ message: 'Internal server error' }), { status: 500 });
  }
}
