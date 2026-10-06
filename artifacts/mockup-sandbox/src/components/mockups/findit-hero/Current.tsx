import "./_group.css";
import { ArrowRight, ArrowUpRight, ShieldCheck } from "lucide-react";

export function Current() {
  return (
    <main className="findit-hero-stage">
      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow">
            <span className="eyebrow-line" /> A community that looks out for you
          </span>
          <h1>
            Lost something?
            <br />
            <em>Let’s bring it home.</em>
          </h1>
          <p>
            Small things matter. FindIt connects the people who’ve misplaced
            something with the kind people who’ve found it.
          </p>
          <div className="hero-actions">
            <a href="#reports" className="button">
              Find an item <ArrowRight size={16} />
            </a>
            <a href="#reports" className="text-link">
              I found something <ArrowUpRight size={16} />
            </a>
          </div>
          <div className="privacy-note">
            <ShieldCheck size={16} />
            <span>Your contact details are never shown publicly.</span>
          </div>
        </div>
        <div className="hero-art" aria-label="Illustration of a found key">
          <div className="art-corner art-corner-top" />
          <div className="art-corner art-corner-bottom" />
          <div className="orbit orbit-one" />
          <div className="orbit orbit-two" />
          <div className="art-sun" />
          <div className="art-key">
            <div className="key-ring" />
            <div className="key-stem" />
            <div className="key-tooth" />
          </div>
          <div className="art-caption">
            <span className="caption-dot" />
            <span>Little things find their way.</span>
          </div>
          <div className="art-stamp">
            RETURN
            <br />
            WITH
            <br />
            CARE
          </div>
        </div>
      </section>
    </main>
  );
}
