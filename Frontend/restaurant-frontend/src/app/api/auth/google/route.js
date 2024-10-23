
import { NextResponse } from 'next/server';
import * as cookie from 'cookie'; // Import everything from cookie
import fetch from 'node-fetch'; // Ensure node-fetch is installed

export async function GET(req) {
  const { searchParams } = new URL(req.url);
  const code = searchParams.get('code');

  if (!code) {
    // After handling the login, redirect to the login if no code returned
    const redirectUrl = `http://localhost:3000/login`;
    return NextResponse.redirect(redirectUrl);
  }

  const tokenUrl = "https://oauth2.googleapis.com/token";
  const data = {
    code: code,
    client_id: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID,
    client_secret: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_SECRET,
    redirect_uri: "http://localhost:3000/api/auth/google",
    grant_type: "authorization_code",
  };

  try {
    const tokenResponse = await fetch(tokenUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams(data).toString(),
    });

    if (!tokenResponse.ok) {
      throw new Error("Failed to fetch token");
    }

    const tokenData = await tokenResponse.json();
    const accessToken = tokenData.access_token;

    // Fetch user info
    const userInfoResponse = await fetch("https://www.googleapis.com/oauth2/v1/userinfo", {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    if (!userInfoResponse.ok) {
      throw new Error("Failed to fetch user info");
    }

    const userInfo = await userInfoResponse.json();

    // After handling the login, redirect to the dashboard
    const redirectUrl = `http://localhost:3000/dashboard`;
    const res = NextResponse.redirect(redirectUrl);

    return res;
  } catch (error) {
    console.error("Error in authentication flow:", error);
    return new NextResponse("Internal Server Error", { status: 500 });
  }
}
