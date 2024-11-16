import { useCallback, useState } from 'react';
import type { Address } from 'viem';
import axios from 'axios';
import { API_URL } from '../config';

type UseGetNFTsResponse = {
  NFTs?: Address[];
  error?: Error;
  getNFTs: () => void;
  isLoading: boolean;
};

type UseGetNFTsProps = {
  onSuccess: (addresses: Address[]) => void;
};

export default function useGetNFTs({
  onSuccess,
}: UseGetNFTsProps): UseGetNFTsResponse {
  const [isLoading, setIsLoading] = useState(false);

  const getNFTs = useCallback(async () => {
    setIsLoading(true);

    try {
      const { data } = await axios.get(`${API_URL}/nfts`, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const { nfts } = data;
      onSuccess(nfts);

      return { nfts, error: null };
    } catch (error) {
      console.error('Error fetching nfts:', error);
      return { nfts: [], error: error as Error };
    } finally {
      setIsLoading(false);
    }
  }, [onSuccess]);

  return { getNFTs, isLoading };
}
