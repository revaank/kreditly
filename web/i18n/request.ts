import { getRequestConfig } from "next-intl/server";
import en from "../messages/en.json";
import hi from "../messages/hi.json";

export default getRequestConfig(async ({ requestLocale }) => {
  const requested = await requestLocale;
  const locale = requested === "hi" ? "hi" : "en";
  return { locale, messages: locale === "hi" ? hi : en };
});
