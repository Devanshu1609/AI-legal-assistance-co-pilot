import React, { useState } from "react";
import { Scale } from "lucide-react";
import { auth } from "../firebase";

import {
  GoogleAuthProvider,
  signInWithPopup,
} from "firebase/auth";

const LoginPage = () => {
  const [loading, setLoading] =
    useState(false);

  const handleGoogleLogin =
    async () => {
      try {
        setLoading(true);

        const provider =
          new GoogleAuthProvider();

        await signInWithPopup(
          auth,
          provider
        );
      } catch (error) {
        console.error(
          "Google Sign-In Error:",
          error
        );
      } finally {
        setLoading(false);
      }
    };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#020817] via-[#071229] to-[#0B1F4D] flex items-center justify-center px-4 relative overflow-hidden">

      {/* Background Glow */}
      <div className="absolute top-0 left-0 w-72 h-72 bg-blue-500 opacity-20 blur-[140px] rounded-full"></div>
      <div className="absolute bottom-0 right-0 w-72 h-72 bg-cyan-500 opacity-20 blur-[140px] rounded-full"></div>

      {/* Login Card */}
      <div className="w-full max-w-md bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl shadow-2xl p-8 relative z-10">

        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-blue-500/10 flex items-center justify-center border border-blue-400/20">
            <Scale
              className="text-blue-400"
              size={30}
            />
          </div>

          <h1 className="text-3xl font-bold text-white mt-4">
            Welcome
          </h1>

          <p className="text-gray-400 mt-2 text-sm text-center">
            Continue with Google to use
            AI Legal Co-Pilot
          </p>
        </div>

        {/* Google Login Button */}
        <button
          onClick={handleGoogleLogin}
          disabled={loading}
          className="w-full py-4 rounded-xl 
          bg-white text-black font-semibold 
          flex items-center justify-center gap-3
          hover:scale-[1.02] transition-all duration-300"
        >
          <img
            src="https://cdn-icons-png.flaticon.com/512/281/281764.png"
            alt="Google"
            className="w-5 h-5"
          />

          {loading
            ? "Signing in..."
            : "Continue with Google"}
        </button>
      </div>
    </div>
  );
};

export default LoginPage;