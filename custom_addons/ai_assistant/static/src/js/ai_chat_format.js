/** @odoo-module **/

const MARKDOWN_LINK_RE = /\[([^\]]+)\]\(([^)]+)\)/g;

/**
 * Extract markdown links from assistant text (fallback when links[] empty).
 * @param {string} content
 * @returns {{label: string, url: string}[]}
 */
export function extractMarkdownLinks(content) {
    if (!content) {
        return [];
    }
    const links = [];
    const seen = new Set();
    let match;
    const re = new RegExp(MARKDOWN_LINK_RE.source, MARKDOWN_LINK_RE.flags);
    while ((match = re.exec(content)) !== null) {
        const label = (match[1] || "").trim();
        const url = (match[2] || "").trim();
        if (!url || url.toLowerCase() === "none" || seen.has(url)) {
            continue;
        }
        seen.add(url);
        links.push({ label: label || url, url });
    }
    return links;
}

/**
 * Merge API links with markdown links, dedupe by url.
 * @param {{label?: string, url?: string}[]} apiLinks
 * @param {string} content
 */
export function mergeMessageLinks(apiLinks, content) {
    const merged = [];
    const seen = new Set();
    for (const link of apiLinks || []) {
        const url = (link && link.url) || "";
        if (!url || seen.has(url)) {
            continue;
        }
        seen.add(url);
        merged.push({
            label: (link.label || url).trim(),
            url,
            menu_breadcrumb: link.menu_breadcrumb || "",
        });
    }
    for (const link of extractMarkdownLinks(content)) {
        if (seen.has(link.url)) {
            continue;
        }
        seen.add(link.url);
        merged.push(link);
    }
    return merged;
}

/**
 * Plain text for bubble: markdown links -> label, drop duplicate raw URLs.
 * @param {string} content
 * @param {{url: string}[]} links
 */
export function formatMessageContent(content, links = []) {
    if (!content) {
        return "";
    }
    let text = content.replace(MARKDOWN_LINK_RE, (_full, label) => label);
    for (const link of links) {
        if (link.url) {
            text = text.split(link.url).join("");
        }
    }
    return text.replace(/\n{3,}/g, "\n\n").trim();
}
