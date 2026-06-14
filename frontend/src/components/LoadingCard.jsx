import capybaraLoading from "../assets/capybara-loading.png";
import { WarmingStrip } from "./WarmingStrip.jsx";

export function LoadingCard({ text }) {
  return (
    <section className="loading-card" role="status" aria-live="polite">
      <img src={capybaraLoading} alt="" />
      <div>
        <strong>{text || "Capy is checking their heart rhythm..."}</strong>
        <span>Warm bath, steady paws, clean ECG grid.</span>
      </div>
      <WarmingStrip compact />
    </section>
  );
}
