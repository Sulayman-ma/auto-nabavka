import { cookies } from "next/headers";

export async function GET(request) {
  try {
    const authHeader = request.headers.get("Authorization")
    const token = authorizationHeader.replace("Bearer ", "");

    // Return unauthorized if token is missing
    if (!token) {
      console.log(token)
      return new Response(JSON.stringify({ message: 'No token found' }), { status: 401 });
    }

    console.log("token found, sending request now");

    // Send GET request to API get fetch all users
    const response = await fetch(
      "https://auto-nabavka.onrender.com/api/users/",
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token.value}`
        }
      }      
    );

    // Return response status and data based on success of operation
    if (!response.ok) {
      return new Response(JSON.stringify({ message: 'Failed to update user' }), { status: 500 });
    }

    const data = await response.json();
    return new Response(JSON.stringify(data), { status: 200 });

  } catch (error) {
    // Catch a server error and return accordingly
    return new Response(JSON.stringify({ message: 'Internal server error', error: error }), { status: 500 });
  }
}
