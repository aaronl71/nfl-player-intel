SELECT 
    COUNT(*) as total,
    COUNT(player_id) as matched,
    COUNT(*) - COUNT(player_id) as unmatched
FROM contracts;





