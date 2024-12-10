'use client';

import { Typography, Input, Button, Spinner } from "@material-tailwind/react";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Page() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Router for navigatoni
  const router = useRouter();

  const handleLogin = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true)

    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const { error } = await response.json();
        setError(error || 'Failed to login');
        setLoading(false)
        return;
      }

      // Navigate to test page on success
      router.push('/dashboard');
    } catch (err) {
      console.error(err);
      setError('An unexpected error occurred');
      setLoading(false)
    }
  };

  return (
    <section className="grid text-center h-screen items-center p-8">
      <div>
        <Typography variant="h3" color="blue-gray" className="mb-2">
          Sign In
        </Typography>
        <Typography className="mb-16 text-gray-600 font-normal text-[18px]">
          Enter your email and password to sign in
        </Typography>
        <form
          onSubmit={handleLogin}
          className="mx-auto max-w-[24rem] text-left"
        >
          <div className="mb-6">
            <label htmlFor="email">
              <Typography
                variant="small"
                className="mb-2 block font-medium text-gray-900"
              >
                Your Email
              </Typography>
            </label>
            <Input
              id="email"
              color="gray"
              size="lg"
              type="email"
              value={username}
              required
              onChange={(e) => setUsername(e.target.value)}
              placeholder="name@mail.com"
              className="w-full placeholder:opacity-100 focus:border-t-primary border-t-blue-gray-200"
              labelProps={{
                className: "hidden",
              }}
            />
          </div>
          <div className="mb-6">
            <label htmlFor="password">
              <Typography
                variant="small"
                className="mb-2 block font-medium text-gray-900"
              >
                Password
              </Typography>
            </label>
            <Input
              size="lg"
              type="password"
              value={password}
              required
              onChange={(e) => setPassword(e.target.value)}
              placeholder="********"
              labelProps={{
                className: "hidden",
              }}
              className="w-full placeholder:opacity-100 focus:border-t-primary border-t-blue-gray-200"
            />
          </div>
          {error && <Typography className="text-red-500 mb-4">{error}</Typography>}
            { loading ? 
              <Button color="gray" size="lg" className="flex items-center justify-center mt-6" fullWidth type="submit" disabled>
                <Spinner />
              </Button>
              : 
              <Button color="gray" size="lg" className="mt-6" fullWidth type="submit">
                Sign In
              </Button>
            }
        </form>
      </div>
    </section>
  );
}
