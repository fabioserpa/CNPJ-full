#!/usr/bin/env sh

if [ ${NO_INDEX} = 1 ]; then
  echo "Starting script using no-index..."
  python cnpj.py "${INPUT_PATH}" ${TYPE_OUTPUT} "${OUTPUT_PATH}" --noindex
fi

if [ ${NO_INDEX} = 0 ]; then
  echo "Starting script..."
  python cnpj.py "${INPUT_PATH}" ${TYPE_OUTPUT} "${OUTPUT_PATH}"
fi

exec "$@"