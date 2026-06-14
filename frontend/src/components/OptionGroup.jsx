export function OptionGroup({ label, value, onChange, options }) {
  return (
    <div className="option-group">
      <span>{label}</span>
      <div className="segmented">
        {options.map((option) => {
          const optionValue = Array.isArray(option) ? option[0] : option;
          const optionLabel = Array.isArray(option) ? option[1] : option;
          return (
            <button
              key={optionValue}
              className={value === optionValue ? "selected" : ""}
              onClick={() => onChange(optionValue)}
              type="button"
            >
              {optionLabel}
            </button>
          );
        })}
      </div>
    </div>
  );
}
