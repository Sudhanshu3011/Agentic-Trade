"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mail, Lock, ArrowRight, User, Eye, EyeOff, X } from "lucide-react";
import { FaGoogle } from "react-icons/fa";
import { Toaster, toast } from "sonner";
import Script from "next/script";
import { AnalysisError, authRequest, authenticateWithGoogle, requestRegistrationOTP, verifyRegistrationOTP, saveAuthSession, type AuthUser } from "@/lib/api";

type Tab = "login" | "signup";
type SignupStep = "details" | "otp_verify";

const colTrans = (delay = 0) => ({
  x: { duration: 0.8, ease: [0.22, 1, 0.36, 1] as const, delay },
  opacity: { duration: 0.8, ease: [0.22, 1, 0.36, 1] as const, delay },
  layout: { type: "spring" as const, stiffness: 220, damping: 26 },
});

export function AuthCard({
  onAuthed,
  onClose,
  initialError,
}: {
  onAuthed: (user: AuthUser) => void;
  onClose?: () => void;
  initialError?: string | null;
}) {
  const [tab, setTab] = useState<Tab>("login");
  const [signupStep, setSignupStep] = useState<SignupStep>("details");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [otpCode, setOtpCode] = useState("");
  const [otpTimer, setOtpTimer] = useState(300); // 5 minutes in seconds
  const [resendCooldown, setResendCooldown] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(initialError || null);

  const successCallbackRef = useRef<any>(null);
  useEffect(() => { successCallbackRef.current = handleGoogleSuccess; });

  // 5-minute countdown timer effect
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    if (tab === "signup" && signupStep === "otp_verify" && otpTimer > 0) {
      interval = setInterval(() => {
        setOtpTimer((prev) => prev - 1);
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [tab, signupStep, otpTimer]);

  // Resend cooldown timer effect
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    if (resendCooldown > 0) {
      interval = setInterval(() => {
        setResendCooldown((prev) => prev - 1);
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [resendCooldown]);

  const handleRequestOTP = async () => {
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      toast.error("Password must be at least 8 characters.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const res = await requestRegistrationOTP({ email, password, name });
      toast.success(res.message || "Verification code sent to your email!");
      setSignupStep("otp_verify");
      setOtpTimer(300); // Reset 5 min timer
      setResendCooldown(30); // 30s resend cooldown
    } catch (err) {
      const errMsg = err instanceof AnalysisError ? err.message : "Unable to send verification code.";
      setError(errMsg);
      toast.error(errMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async () => {
    if (otpCode.trim().length !== 6) {
      setError("Please enter a valid 6-digit verification code.");
      toast.error("Please enter a valid 6-digit verification code.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const session = await verifyRegistrationOTP({ email, otpCode: otpCode.trim() });
      saveAuthSession(session);
      toast.success("Account created and verified successfully!");
      onAuthed(session.user);
    } catch (err) {
      const errMsg = err instanceof AnalysisError ? err.message : "OTP verification failed.";
      setError(errMsg);
      toast.error(errMsg);
    } finally {
      setLoading(false);
    }
  };

  const submit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);

    if (tab === "login") {
      if (password.length < 8) {
        setError("Password must be at least 8 characters.");
        toast.error("Password must be at least 8 characters.");
        return;
      }
      setLoading(true);
      try {
        const session = await authRequest({ mode: "login", email, password });
        saveAuthSession(session);
        toast.success("Logged in successfully!");
        onAuthed(session.user);
      } catch (err) {
        const errMsg = err instanceof AnalysisError ? err.message : "Unable to authenticate right now.";
        setError(errMsg);
        toast.error(errMsg);
      } finally {
        setLoading(false);
      }
    } else {
      if (signupStep === "details") {
        await handleRequestOTP();
      } else {
        await handleVerifyOTP();
      }
    }
  };

  const handleForgotPassword = (e: React.MouseEvent) => {
    e.preventDefault();
    toast.info("Password reset link is not configured for local dev.");
  };

  const handleGoogleSuccess = async (response: any) => {
    setLoading(true);
    setError(null);
    try {
      const session = await authenticateWithGoogle(response.credential);
      saveAuthSession(session);
      toast.success("Signed in with Google successfully!");
      onAuthed(session.user);
    } catch (err) {
      const errMsg = err instanceof AnalysisError ? err.message : "Google sign in failed.";
      setError(errMsg);
      toast.error(errMsg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const initGoogleGis = () => {
      const google = (window as any).google;
      if (google) {
        if (!(window as any).__googleGisInitialized) {
          google.accounts.id.initialize({
            client_id: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID,
            callback: (res: any) => successCallbackRef.current?.(res),
            auto_select: false,
          });
          (window as any).__googleGisInitialized = true;
        }
        const btnEl = document.getElementById("google-signin-btn");
        if (btnEl) {
          google.accounts.id.renderButton(btnEl, {
            theme: "filled_black",
            size: "large",
            width: 312,
            text: "continue_with",
            shape: "rectangular",
          });
        } else {
          setTimeout(initGoogleGis, 100);
        }
      }
    };

    if ((window as any).google) {
      initGoogleGis();
    } else {
      window.addEventListener("google-gis-loaded", initGoogleGis);
    }
    return () => window.removeEventListener("google-gis-loaded", initGoogleGis);
  }, []);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/45 backdrop-blur-md px-4 py-8 overflow-y-auto">
      <Script
        src="https://accounts.google.com/gsi/client"
        strategy="afterInteractive"
        onLoad={() => window.dispatchEvent(new Event("google-gis-loaded"))}
      />
      <Toaster richColors position="top-center" />

      {/* Floating particles inside modal context */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        {Array.from({ length: 10 }).map((_, i) => (
          <motion.span
            key={i}
            className="absolute h-1 w-1 rounded-full bg-[#d4a84c]/60"
            style={{ left: `${(i * 37 + 12) % 100}%`, top: `${(i * 43 + 19) % 100}%` }}
            animate={{ y: [0, -30, 0], opacity: [0.2, 1, 0.2] }}
            transition={{ duration: 4 + (i % 3), repeat: Infinity, delay: i * 0.4, ease: "easeInOut" }}
          />
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 15 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 15 }}
        transition={{ duration: 0.3, ease: "easeOut" }}
        className="relative w-full max-w-[380px] rounded-2xl border border-black/10 bg-white/95 pt-10 sm:pt-12 pb-6 px-4 sm:px-6 shadow-[0_25px_60px_-15px_rgba(0,0,0,0.3)] backdrop-blur-xl max-h-[90vh] overflow-y-auto flex flex-col justify-between"
      >
        {/* Gold border glow */}
        <div className="pointer-events-none absolute inset-0 rounded-2xl bg-gradient-to-br from-[#d4a84c]/20 via-transparent to-black/10 opacity-50 [mask:linear-gradient(#000,#000)_content-box,linear-gradient(#000,#000)] [mask-composite:exclude] p-px" />

        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="absolute right-4 top-4 z-20 text-neutral-400 hover:text-black transition-colors cursor-pointer"
            aria-label="Close"
          >
            <X size={16} />
          </button>
        )}

        {/* Modal Header */}
        <div className="text-center mb-6">
          <h1 className="text-xl font-bold tracking-tight text-black font-sans">Artha Analytics</h1>
          <p className="mt-1 text-[10px] font-semibold tracking-wider text-[#d4a84c] font-mono">Multi-Agent AI. Singular Market Edge</p>
        </div>

        {/* Tabs */}
        <div className="relative mb-5 grid grid-cols-2 rounded-lg border border-black/10 bg-neutral-100/60 p-1">
          {(["login", "signup"] as Tab[]).map((t) => (
            <button
              key={t}
              id={`tab-${t}-btn`}
              onClick={() => { setTab(t); setError(null); }}
              className={`relative z-10 py-2 text-xs font-semibold tracking-[0.2em] transition-colors ${tab === t ? "text-white" : "text-neutral-600 hover:text-black"}`}
            >
              {t.toUpperCase()}
            </button>
          ))}
          <motion.div
            layout
            transition={{ type: "spring", stiffness: 400, damping: 35 }}
            className="absolute inset-y-1 w-1/2 rounded-md bg-black shadow"
            style={{ left: tab === "login" ? "0.25rem" : "calc(50% - 0.25rem)" }}
          />
        </div>

        {/* Form */}
        <AnimatePresence mode="wait">
          <motion.form
            key={tab + (tab === "signup" ? `_${signupStep}` : "")}
            initial={{ opacity: 0, x: tab === "login" ? -15 : 15 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: tab === "login" ? 15 : -15 }}
            transition={{ duration: 0.25 }}
            className="flex-1 flex flex-col justify-between"
            onSubmit={submit}
          >
            <div className="space-y-3.5">
              {tab === "signup" && signupStep === "otp_verify" ? (
                <>
                  <div className="rounded-lg bg-amber-500/10 border border-amber-500/20 p-3 text-center">
                    <p className="text-[11px] text-neutral-600 leading-snug">
                      We sent a 6-digit code to <strong className="text-black font-semibold">{email}</strong>
                    </p>
                  </div>
                  <div className="group">
                    <label className="mb-1 block text-[9px] font-semibold tracking-[0.2em] text-neutral-500">
                      ENTER 6-DIGIT CODE
                    </label>
                    <input
                      id="otp-code-input"
                      type="text"
                      inputMode="numeric"
                      maxLength={6}
                      placeholder="123456"
                      value={otpCode}
                      onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, ""))}
                      autoFocus
                      required
                      className="w-full text-center font-mono text-2xl font-bold tracking-[0.5em] py-2.5 rounded-lg border border-black/10 bg-white/80 text-black placeholder:text-neutral-300 transition-all focus:border-[#d4a84c] focus:bg-white focus:outline-none focus:ring-4 focus:ring-[#d4a84c]/15"
                    />
                  </div>
                  <div className="flex items-center justify-between text-[11px] font-mono text-neutral-500 pt-1">
                    <span>
                      Expires in:{" "}
                      <strong className={otpTimer > 0 ? "text-amber-600 font-bold" : "text-red-600 font-bold"}>
                        {Math.floor(otpTimer / 60).toString().padStart(2, "0")}:{(otpTimer % 60).toString().padStart(2, "0")}
                      </strong>
                    </span>
                    <button
                      type="button"
                      disabled={resendCooldown > 0 || loading}
                      onClick={handleRequestOTP}
                      className="text-[#d4a84c] font-semibold hover:underline disabled:opacity-50 cursor-pointer"
                    >
                      {resendCooldown > 0 ? `Resend (${resendCooldown}s)` : "Resend Code"}
                    </button>
                  </div>
                  <div className="flex justify-center pt-1">
                    <button
                      type="button"
                      onClick={() => { setSignupStep("details"); setError(null); }}
                      className="text-[11px] text-neutral-400 hover:text-black transition-colors"
                    >
                      ← Change details
                    </button>
                  </div>
                </>
              ) : (
                <>
                  {tab === "signup" && (
                    <Field
                      id="signup-name-input"
                      icon={<User size={14} />}
                      label="NAME"
                      type="text"
                      placeholder="Jane Doe"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                    />
                  )}
                  <Field
                    id="auth-email-input"
                    icon={<Mail size={14} />}
                    label="EMAIL"
                    type="email"
                    placeholder="user@gmail.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                  <Field
                    id="auth-password-input"
                    icon={<Lock size={14} />}
                    label="PASSWORD"
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    minLength={8}
                    autoComplete={tab === "login" ? "current-password" : "new-password"}
                  />
                  {tab === "login" && (
                    <div className="flex justify-end">
                      <a id="forgot-password-link" href="#" onClick={handleForgotPassword} className="text-[11px] text-neutral-500 transition-colors hover:text-[#d4a84c]">
                        Forgot password?
                      </a>
                    </div>
                  )}
                </>
              )}
            </div>

            <div className="space-y-3 mt-5">
              {error && (
                <motion.p
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  onClick={() => {
                    if (error.includes("LOGIN")) {
                      setTab("login");
                      setError(null);
                    }
                  }}
                  className={`text-xs font-semibold text-red-500 text-center tracking-wide ${
                    error.includes("LOGIN") ? "cursor-pointer hover:underline" : ""
                  }`}
                >
                  {error}
                </motion.p>
              )}
              <motion.button
                id="auth-submit-btn"
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                type="submit"
                disabled={loading}
                className="group relative w-full overflow-hidden rounded-lg bg-black py-2.5 text-xs font-semibold tracking-[0.3em] text-white disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer"
              >
                <span className="relative z-10 flex items-center justify-center gap-1.5">
                  {loading
                    ? "PLEASE WAIT..."
                    : tab === "login"
                    ? "LOGIN"
                    : signupStep === "details"
                    ? "SEND CODE"
                    : "VERIFY & CREATE ACCOUNT"}
                  {!loading && <ArrowRight size={14} className="transition-transform group-hover:translate-x-1" />}
                </span>
                {!loading && (
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-[#d4a84c] via-[#f0c97a] to-[#d4a84c]"
                    initial={{ x: "-100%" }}
                    whileHover={{ x: 0 }}
                    transition={{ duration: 0.4 }}
                  />
                )}
              </motion.button>
            </div>
          </motion.form>
        </AnimatePresence>

        <div className="my-3.5 flex-shrink-0 flex items-center gap-3">
          <div className="h-px flex-1 bg-black/10" />
          <span className="text-[9px] tracking-[0.3em] text-neutral-400">OR</span>
          <div className="h-px flex-1 bg-black/10" />
        </div>

        <div className="w-full flex-shrink-0 flex justify-center mt-1">
          {/* Native Google Sign-In Button */}
          <div id="google-signin-btn" />
        </div>
      </motion.div>
    </div>
  );
}

interface FieldProps {
  icon: React.ReactNode;
  label: string;
  type: string;
  placeholder: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  id: string;
  required?: boolean;
  minLength?: number;
  autoComplete?: string;
}

function Field({ icon, label, type, placeholder, value, onChange, id, required, minLength, autoComplete }: FieldProps) {
  const [showPassword, setShowPassword] = useState(false);
  const isPassword = type === "password";
  const inputType = isPassword ? (showPassword ? "text" : "password") : type;

  return (
    <div className="group">
      <label className="mb-1 block text-[9px] font-semibold tracking-[0.2em] text-neutral-500">{label}</label>
      <div className="relative">
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400 transition-colors group-focus-within:text-[#d4a84c]">{icon}</span>
        <input
          id={id}
          type={inputType}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          required={required}
          minLength={minLength}
          autoComplete={autoComplete}
          className="w-full rounded-lg border border-black/10 bg-white/60 py-2.5 pl-9 pr-10 text-sm text-black placeholder:text-neutral-400 transition-all focus:border-[#d4a84c] focus:bg-white focus:outline-none focus:ring-4 focus:ring-[#d4a84c]/15"
        />
        {isPassword && (
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-black transition-colors"
          >
            {showPassword ? <EyeOff size={14} /> : <Eye size={14} />}
          </button>
        )}
      </div>
    </div>
  );
}
