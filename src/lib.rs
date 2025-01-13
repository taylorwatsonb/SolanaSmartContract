use borsh::{BorshDeserialize, BorshSerialize};
use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    program_error::ProgramError,
    pubkey::Pubkey,
};

#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub struct TokenAccount {
    pub owner: Pubkey,
    pub amount: u64,
    pub mint_authority: Option<Pubkey>,
}

#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub enum TokenInstruction {
    InitializeAccount,
    Transfer { amount: u64 },
    Mint { amount: u64 },
    Burn { amount: u64 },
}

entrypoint!(process_instruction);

pub fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    msg!("Token program entrypoint");

    let instruction = TokenInstruction::try_from_slice(instruction_data)
        .map_err(|_| ProgramError::InvalidInstructionData)?;

    match instruction {
        TokenInstruction::InitializeAccount => {
            msg!("Instruction: InitializeAccount");
            process_initialize_account(program_id, accounts)
        }
        TokenInstruction::Transfer { amount } => {
            msg!("Instruction: Transfer");
            process_transfer(accounts, amount)
        }
        TokenInstruction::Mint { amount } => {
            msg!("Instruction: Mint");
            process_mint(accounts, amount)
        }
        TokenInstruction::Burn { amount } => {
            msg!("Instruction: Burn");
            process_burn(accounts, amount)
        }
    }
}

fn process_initialize_account(program_id: &Pubkey, accounts: &[AccountInfo]) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let account = next_account_info(account_info_iter)?;
    let mint_authority = next_account_info(account_info_iter)?;

    if account.owner != program_id {
        msg!("Account owner is not the program");
        return Err(ProgramError::IncorrectProgramId);
    }

    let token_account = TokenAccount {
        owner: *account.key,
        amount: 0,
        mint_authority: Some(*mint_authority.key),
    };

    token_account.serialize(&mut *account.data.borrow_mut())?;
    msg!("Account initialized successfully");
    Ok(())
}

fn process_transfer(accounts: &[AccountInfo], amount: u64) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let source_account = next_account_info(account_info_iter)?;
    let destination_account = next_account_info(account_info_iter)?;

    let mut source_data = TokenAccount::try_from_slice(&source_account.data.borrow())?;
    let mut dest_data = TokenAccount::try_from_slice(&destination_account.data.borrow())?;

    if source_data.amount < amount {
        msg!("Insufficient funds for transfer");
        return Err(ProgramError::InsufficientFunds);
    }

    source_data.amount = source_data
        .amount
        .checked_sub(amount)
        .ok_or_else(|| {
            msg!("Error: Underflow in source account balance");
            ProgramError::InvalidArgument
        })?;

    dest_data.amount = dest_data
        .amount
        .checked_add(amount)
        .ok_or_else(|| {
            msg!("Error: Overflow in destination account balance");
            ProgramError::InvalidArgument
        })?;

    source_data.serialize(&mut *source_account.data.borrow_mut())?;
    dest_data.serialize(&mut *destination_account.data.borrow_mut())?;

    msg!("Transfer completed successfully");
    Ok(())
}

fn process_mint(accounts: &[AccountInfo], amount: u64) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let token_account = next_account_info(account_info_iter)?;
    let authority = next_account_info(account_info_iter)?;

    let mut account_data = TokenAccount::try_from_slice(&token_account.data.borrow())?;

    // Verify mint authority
    if account_data.mint_authority.is_none() || account_data.mint_authority.unwrap() != *authority.key {
        msg!("Invalid mint authority");
        return Err(ProgramError::InvalidArgument);
    }

    // Add tokens
    account_data.amount = account_data
        .amount
        .checked_add(amount)
        .ok_or_else(|| {
            msg!("Error: Overflow while minting");
            ProgramError::InvalidArgument
        })?;

    account_data.serialize(&mut *token_account.data.borrow_mut())?;
    msg!("Minted {} tokens successfully", amount);
    Ok(())
}

fn process_burn(accounts: &[AccountInfo], amount: u64) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let token_account = next_account_info(account_info_iter)?;
    let owner = next_account_info(account_info_iter)?;

    let mut account_data = TokenAccount::try_from_slice(&token_account.data.borrow())?;

    // Verify owner
    if account_data.owner != *owner.key {
        msg!("Invalid account owner");
        return Err(ProgramError::InvalidArgument);
    }

    // Verify sufficient balance
    if account_data.amount < amount {
        msg!("Insufficient balance for burning");
        return Err(ProgramError::InsufficientFunds);
    }

    // Burn tokens
    account_data.amount = account_data
        .amount
        .checked_sub(amount)
        .ok_or_else(|| {
            msg!("Error: Underflow while burning");
            ProgramError::InvalidArgument
        })?;

    account_data.serialize(&mut *token_account.data.borrow_mut())?;
    msg!("Burned {} tokens successfully", amount);
    Ok(())
}

#[cfg(test)]
mod test {
    use super::*;
    use solana_program::clock::Epoch;
    use std::mem;

    #[test]
    fn test_initialize_account() {
        let program_id = Pubkey::default();
        let key = Pubkey::default();
        let mint_authority_key = Pubkey::default();
        let mut lamports = 0;
        let mut data = vec![0; mem::size_of::<TokenAccount>()];
        let mut auth_lamports = 0;
        let mut auth_data = vec![0; mem::size_of::<TokenAccount>()];
        let owner = program_id;

        let account = AccountInfo::new(
            &key,
            false,
            true,
            &mut lamports,
            &mut data,
            &owner,
            false,
            Epoch::default(),
        );

        let mint_authority = AccountInfo::new(
            &mint_authority_key,
            false,
            false,
            &mut auth_lamports,
            &mut auth_data,
            &owner,
            false,
            Epoch::default(),
        );

        let accounts = vec![account, mint_authority];
        let result = process_initialize_account(&program_id, &accounts);
        assert!(result.is_ok());
    }

    #[test]
    fn test_mint_and_burn() {
        let program_id = Pubkey::new_unique();
        let key = Pubkey::new_unique();
        let mint_authority = Pubkey::new_unique();
        let owner = Pubkey::new_unique();

        // Initialize account
        {
            let mut lamports = 0;
            let mut data = vec![0u8; mem::size_of::<TokenAccount>()];
            let mut auth_lamports = 0;
            let mut auth_data = vec![0u8; mem::size_of::<TokenAccount>()];

            let account = AccountInfo::new(
                &key,
                false,
                true,
                &mut lamports,
                &mut data,
                &program_id,
                false,
                Epoch::default(),
            );

            let mint_authority_info = AccountInfo::new(
                &mint_authority,
                false,
                false,
                &mut auth_lamports,
                &mut auth_data,
                &program_id,
                false,
                Epoch::default(),
            );

            let accounts = vec![account, mint_authority_info];
            process_initialize_account(&program_id, &accounts).unwrap();

            // Verify initialization
            let account_data = TokenAccount::try_from_slice(&data).unwrap();
            assert_eq!(account_data.amount, 0);
            assert_eq!(account_data.mint_authority.unwrap(), mint_authority);
        }

        // Mint tokens
        {
            let mut lamports = 0;
            let mut data = vec![0u8; mem::size_of::<TokenAccount>()];
            let mut auth_lamports = 0;
            let mut auth_data = vec![0u8; mem::size_of::<TokenAccount>()];

            // Initialize account data with proper structure
            let token_account = TokenAccount {
                owner: key,
                amount: 0,
                mint_authority: Some(mint_authority),
            };
            token_account.serialize(&mut data).unwrap();

            let account = AccountInfo::new(
                &key,
                false,
                true,
                &mut lamports,
                &mut data,
                &program_id,
                false,
                Epoch::default(),
            );

            let mint_authority_info = AccountInfo::new(
                &mint_authority,
                false,
                false,
                &mut auth_lamports,
                &mut auth_data,
                &program_id,
                false,
                Epoch::default(),
            );

            let accounts = vec![account, mint_authority_info];
            let mint_amount = 100;
            let instruction = TokenInstruction::Mint { amount: mint_amount };
            let instruction_data = instruction.try_to_vec().unwrap();
            process_instruction(&program_id, &accounts, &instruction_data).unwrap();

            // Verify mint
            let account_data = TokenAccount::try_from_slice(&data).unwrap();
            assert_eq!(account_data.amount, mint_amount);
        }

        // Burn tokens
        {
            let mut lamports = 0;
            let mut data = vec![0u8; mem::size_of::<TokenAccount>()];
            let mut owner_lamports = 0;
            let mut owner_data = vec![0u8; mem::size_of::<TokenAccount>()];

            // Initialize account data with proper structure and minted amount
            let token_account = TokenAccount {
                owner: owner,
                amount: 100,
                mint_authority: Some(mint_authority),
            };
            token_account.serialize(&mut data).unwrap();

            let account = AccountInfo::new(
                &key,
                false,
                true,
                &mut lamports,
                &mut data,
                &program_id,
                false,
                Epoch::default(),
            );

            let owner_info = AccountInfo::new(
                &owner,
                false,
                false,
                &mut owner_lamports,
                &mut owner_data,
                &program_id,
                false,
                Epoch::default(),
            );

            let accounts = vec![account, owner_info];
            let burn_amount = 50;
            let instruction = TokenInstruction::Burn { amount: burn_amount };
            let instruction_data = instruction.try_to_vec().unwrap();
            process_instruction(&program_id, &accounts, &instruction_data).unwrap();

            // Verify burn
            let account_data = TokenAccount::try_from_slice(&data).unwrap();
            assert_eq!(account_data.amount, 50); // 100 - 50 = 50
        }
    }
}