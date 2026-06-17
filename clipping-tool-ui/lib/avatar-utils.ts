import { AvatarGenerator } from "random-avatar-generator";

const generator = new AvatarGenerator();

/**
 * Generate a consistent avatar URL based on a seed (like user email)
 * @param seed - The seed to generate a consistent avatar (e.g., user email)
 * @returns Avatar URL string
 */
export function generateAvatar(seed: string): string {
  return generator.generateRandomAvatar(seed);
}

/**
 * Generate a random avatar URL
 * @returns Random avatar URL string
 */
export function generateRandomAvatar(): string {
  return generator.generateRandomAvatar();
}
