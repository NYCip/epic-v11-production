// src/types/next-auth.d.ts
import NextAuth, { DefaultSession, DefaultUser } from "next-auth"
import { JWT } from "next-auth/jwt"

// Extend the User type to include custom properties from your API
declare module "next-auth" {
  interface User extends DefaultUser {
    id: string; // From your API response
    email: string; // From your API response
    role: 'admin' | 'operator' | 'viewer'; // From your API response
    accessToken: string; // Custom property
  }

  // Extend the Session type to include custom properties
  interface Session extends DefaultSession {
    accessToken: string;
    user: {
      id: string;
      email: string;
      role: 'admin' | 'operator' | 'viewer';
    } & DefaultSession['user']; // Preserve existing DefaultSession user properties
  }
}

// Extend the JWT type to include custom properties stored in the token
declare module "next-auth/jwt" {
  interface JWT {
    id: string;
    email: string;
    role: 'admin' | 'operator' | 'viewer';
    accessToken: string;
  }
}