import i18n from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import { initReactI18next } from "react-i18next";

import { en } from "./en";
import { vi } from "./vi";

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      vi: { translation: vi },
      en: { translation: en },
    },
    fallbackLng: "vi",
    interpolation: { escapeValue: false },
    detection: {
      order: ["localStorage", "navigator"],
      lookupLocalStorage: "vcc_locale",
      caches: ["localStorage"],
    },
  });

export default i18n;

// Re-export for backward compatibility
export type Locale = "vi" | "en";
export { useTranslation } from "react-i18next";
