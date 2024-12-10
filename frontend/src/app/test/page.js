import { cookies } from "next/headers"

export default async function Page() {
  const token = (await cookies()).get("token")
  return (
    <>
      {token ? JSON.stringify(token.value) : "No token available"}
    </>
  )
}
