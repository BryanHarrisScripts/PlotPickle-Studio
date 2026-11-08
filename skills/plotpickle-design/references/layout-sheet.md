# Production design sheet templates

Character 3x3: front, three-quarter left, profile, back, three-quarter right, expression study, wardrobe, hands/props, silhouette. Every panel is a square view (1:1). Separate sheets for distinct source-grounded age periods, not an undifferentiated mix of child/adult reference images. Keep the accepted facial identity, build and clothing signatures stable across all camera angles. Expressions and costumes are reviewable proposals until approved.

World 2 columns × 3 rows: establishing, ground plan, reverse, detail, lighting, spatial anchors. Every panel is 16:9. Lock a consistent compass, entrance/exit, horizon and props only after author review. Do not infer an architectural plan from a single still or a screenplay time card.

Plan JSON `plotpickle.design-layout.v1` includes project id/revision/SHA, subject, source passage IDs, cells and approval flags. HTML `sheet` is a printable index of missing image positions; it is not a media composite. When host-native image generation supplies a candidate image, inspect it, get actual bytes and hash, and stage it with the same project ID, revision, sheet type, subject ID and panel ID. A candidate cannot become `imageVerified: true` or `designApproved: true` just because the user asks to view the sheet. All approvals and durable writes require separately supported host operations.
