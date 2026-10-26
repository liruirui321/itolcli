# iTOL batch operations

Source of truth: [official batch help](https://itol.embl.de/help.cgi#batch). Checked 2026-10-26.

Upload sends a multipart POST to `https://itol.embl.de/batch_uploader.cgi`. Native CLI reads `ITOL_API_KEY` and uses `--project`; the server requires an active Standard subscription. The ZIP contains a recognized tree filename and ordered annotation files. `--dry-run` builds the same archive without sending it. Native upload returns `tree_id`, URL and server warnings.

Export sends form data to `https://itol.embl.de/batch_downloader.cgi`. Native formats are SVG/PDF/PNG/EPS/Newick/Nexus/PhyloXML. Additional render options pass through to iTOL. The CLI rejects error pages and mismatched file signatures before saving. An HTTP 200 is not enough to establish success. Subscription-free export does not grant access to otherwise unavailable trees.

Wait at least a few seconds between requests, especially image exports. Upload requests are not retried automatically; after a network timeout inspect the project before retrying. Native client throttling applies within one client instance, so external loops must also be paced.

Never include API keys in annotations, export config, commits or output reports. A missing key, subscription or project is a concrete prerequisite for real upload, not evidence that local annotation generation failed.

An export changes the downloaded representation; passing style settings to the downloader does not establish that those settings have been saved to the remote tree. To retain web edits, follow iTOL's account and save rules. Website support, official API support and a third-party wrapper's advertised options are separate claims; verify an option against the official endpoint before relying on it.
