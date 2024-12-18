#!/bin/bash  

find ../images -type f -print0 | while IFS= read -r -d $'\0' file; do
  filename=$(basename "$file")

  response=$(curl -s -X POST "https://comp3211cwkthumbnail.azurewebsites.net/api/GetThumbnail" \
    -H "Content-Type: multipart/form-data" \
    -F "image=@\"../images/$filename\"")

  echo "Link: $response" >> captions.txt

  url=$(echo "$response" | tr -d '\n')

  caption=$(curl -s -X POST "https://comp3211cwkthumbnail.azurewebsites.net/api/GetCaption" \
    -H "Content-Type: application/json" \
    -d '{"url":"'"$url"'"}')

  echo "Caption: $caption" >> captions.txt

  echo "$caption"
done

echo "Finished captioning images."
