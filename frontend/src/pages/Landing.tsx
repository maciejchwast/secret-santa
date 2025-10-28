import { motion } from "framer-motion";
import { useState } from "react";
import { createGroup, GroupCreatePayload } from "../api/groups";

export function LandingPage() {
  const [form, setForm] = useState<GroupCreatePayload>({
    name: "",
    organizer_email: "",
    budget: undefined,
    reveal_date: "",
    allow_household: false
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<null | {
    join_url: string;
    join_pin: string;
    join_token: string;
    group_id: string;
  }>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const payload: GroupCreatePayload = {
        name: form.name,
        organizer_email: form.organizer_email,
        budget: form.budget,
        reveal_date: form.reveal_date || undefined,
        allow_household: form.allow_household
      };
      const data = await createGroup(payload);
      setResult({ ...data, group_id: data.group_id });
    } catch (err) {
      setError("Could not create group. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-16">
      <motion.div
        className="max-w-2xl w-full bg-slate-800/80 rounded-3xl shadow-2xl p-10 space-y-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="space-y-2 text-center">
          <motion.h1 className="text-4xl font-bold text-santa-gold" layoutId="headline">
            Secret Santa Organizer
          </motion.h1>
          <p className="text-slate-200">
            Create a private Secret Santa group, invite participants, and let us handle the draw and notifications.
          </p>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit}>
          <div>
            <label className="block text-sm font-semibold text-slate-200">Group name</label>
            <input
              className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900/60 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-santa-gold"
              value={form.name}
              onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-200">Organizer email</label>
            <input
              type="email"
              className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900/60 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-santa-gold"
              value={form.organizer_email}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, organizer_email: event.target.value }))
              }
              required
            />
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label className="block text-sm font-semibold text-slate-200">Budget (optional)</label>
              <input
                type="number"
                min={0}
                className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900/60 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-santa-gold"
                value={form.budget ?? ""}
                onChange={(event) =>
                  setForm((prev) => ({
                    ...prev,
                    budget: event.target.value ? Number(event.target.value) : undefined
                  }))
                }
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-200">Reveal date</label>
              <input
                type="datetime-local"
                className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900/60 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-santa-gold"
                value={form.reveal_date || ""}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, reveal_date: event.target.value }))
                }
              />
            </div>
          </div>
          <label className="inline-flex items-center space-x-2">
            <input
              type="checkbox"
              className="h-5 w-5 rounded border border-slate-700 bg-slate-900/60 text-santa-gold focus:ring-santa-gold"
              checked={form.allow_household}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, allow_household: event.target.checked }))
              }
            />
            <span className="text-sm text-slate-200">Allow gifting within the same household</span>
          </label>
          <motion.button
            whileTap={{ scale: 0.98 }}
            className="w-full rounded-xl bg-santa-red px-4 py-3 text-lg font-semibold text-white shadow-lg shadow-santa-red/30 transition hover:bg-santa-red/90"
            type="submit"
            disabled={loading}
          >
            {loading ? "Creating..." : "Create group"}
          </motion.button>
        </form>

        {error && <p className="text-center text-sm text-red-400">{error}</p>}

        {result && (
          <motion.div
            className="rounded-2xl border border-santa-gold/40 bg-slate-900/70 p-6 text-sm text-slate-200"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h2 className="text-lg font-semibold text-santa-gold">Group ready!</h2>
            <p className="mt-2">
              Share this URL with participants:
              <span className="mt-1 block break-words font-mono text-santa-gold">
                {result.join_url}
              </span>
            </p>
            <p className="mt-2">Join PIN: {result.join_pin}</p>
            <p className="mt-2 text-xs text-slate-400">
              Store the join token securely. You will need it for participants to join.
            </p>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}
