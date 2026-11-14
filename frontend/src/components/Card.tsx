import type { HTMLAttributes } from "react";
import styles from "./Card.module.css";

interface CardProps extends HTMLAttributes<HTMLElement> {
  as?: "section" | "article" | "div" | "li";
  padding?: "md" | "lg";
}

export function Card({ as: Tag = "div", padding = "md", className, ...rest }: CardProps) {
  return (
    <Tag
      className={[styles.card, styles[padding], className].filter(Boolean).join(" ")}
      {...rest}
    />
  );
}
