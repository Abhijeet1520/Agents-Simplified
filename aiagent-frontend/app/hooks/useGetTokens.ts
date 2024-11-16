import { useCallback, useState } from 'react';
import type { Address } from 'viem';
import axios from 'axios';
import { API_URL } from '../config';

type UseGetTokensResponse = {
  tokens?: Address[];
  error?: Error;
  getTokens: () => void;
  isLoading: boolean;
};

type UseGetTokensProps = {
  onSuccess?: (tokens: Address[]) => void;
};

export default function useGetTokens({
  onSuccess,
}: UseGetTokensProps): UseGetTokensResponse {
  const [isLoading, setIsLoading] = useState(false);

  const getTokens = useCallback(async () => {
    setIsLoading(true);

    try {
      const { data } = await axios.get(`${API_URL}/tokens`, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const { tokens } = data;
      onSuccess?.(tokens);
      return { tokens, error: null };
    } catch (error) {
      console.error('Error fetching tokens:', error);
      return { tokens: [], error: error as Error };
    } finally {
      setIsLoading(false);
    }
  }, [onSuccess]);

  return { getTokens, isLoading };
}
