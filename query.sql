SELECT page.page_title, revision.rev_timestamp, MIN(created.rev_timestamp), COUNT(DISTINCT(comments.rev_actor)) 
FROM page INNER JOIN revision ON page.page_latest = revision.rev_id 
INNER JOIN revision AS created ON page.page_id = created.rev_page 
INNER JOIN revision AS comments ON page.page_id = comments.rev_page 
WHERE page.page_namespace = 4  
AND page.page_title LIKE 'Törlésre_javasolt_lapok/%' 
AND page.page_id NOT IN ( SELECT tl_from FROM templatelinks INNER JOIN linktarget ON tl_target_id = lt_id WHERE lt_title = 'Ta' OR lt_title = 'Lt' OR lt_title = 'Kiürített_lap' ) 
AND page.page_title IN ( SELECT linktarget.lt_title FROM templatelinks INNER JOIN linktarget ON tl_target_id = lt_id WHERE tl_from = 362 ) 
AND page.page_is_redirect = 0 
AND page_title <> 'Törlésre_javasolt_lapok/fej' 
GROUP BY page.page_title 
ORDER BY MIN(created.rev_timestamp) DESC;
